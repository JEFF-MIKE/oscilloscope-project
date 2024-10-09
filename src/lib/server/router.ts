import { initTRPC } from '@trpc/server'; 
import type { Context } from '$lib/server/context';
import { TRPCError } from '@trpc/server';
import { scopeAcquireGraphData, scopeGenericQueryHandler, scopeGenericWriteHandler, generateRandomizedSquareWave } from './scopeFunctions/scopeFunctions';
import z from 'zod';
import { createNewSession, sessionList} from './scopeFunctions/scopeSessionFunctions';

const tRpcServer = initTRPC.context<Context>().create();

const scopeInputSchema = z.object({
    message: z.string()
});

const connectionProcedure = tRpcServer.procedure.use(async function isNIVisaDeviceConnected(opts) {
    if (sessionList.length === 0) {
        try {
            createNewSession();
        } catch (err) {
            throw new TRPCError({
                code: 'INTERNAL_SERVER_ERROR',
                message: "Couldn't establish connection to NIVisa device!",
                cause: err
            });
        }
    }
    return opts.next({
        ctx: {
            deviceSession: sessionList[0],
        }
    });
});

export const router = tRpcServer.router({
    example: connectionProcedure.query(async ({ctx: { deviceSession }}) => {
        return `Hello from tRPC server: Your device session is: ${deviceSession}`;
    }),
    scopeGenericQueryHandler: connectionProcedure.input(scopeInputSchema).query(async ({ ctx: { deviceSession }, input: { message } }) => {
        console.log(`Querying device with message: ${message}`);
        let response;
        try {
            response = scopeGenericQueryHandler(deviceSession, message);
        } catch (err) {
            // Convert this to an error thrown by tRPC server.
            throw new TRPCError({
                code: 'INTERNAL_SERVER_ERROR',
                message: "An unexpected error executing your request, please try again later!",
                cause: err
            });
        }
        return response;
    }),
    scopeGenericWriteHandler: connectionProcedure.input(scopeInputSchema).mutation(async ({ ctx: { deviceSession }, input: { message } }) => {
        console.log(`Server: Writing to device with message: ${message}`);
        let response;
        try {
            response = scopeGenericWriteHandler(deviceSession, message);
        } catch (err) {
            throw new TRPCError({
                code: 'INTERNAL_SERVER_ERROR',
                message: "An unexpected error occured with executing your command, please try again later!",
                cause: err
            })
        }
        return response;
    }),
    scopeAcquireGraphData: connectionProcedure.query(async ({ ctx: { deviceSession } }) => {
        // Graph data aquisition is more tedious, encapsulate it in a function of its own
        console.log(`Server: Acquiring graph data...`);
        let response;
        try {
            response = scopeAcquireGraphData(deviceSession);
        } catch (err) {
            throw new TRPCError({
                code: 'INTERNAL_SERVER_ERROR',
                message: "An unexpected error occured with acquiring graph data, please try again later!",
                cause: err,
            });
        }
        return response;
    }),
    randomizedWaveformData: tRpcServer.procedure.query(async() => {
        return generateRandomizedSquareWave(1, 100);
    })
});

export const createCaller = tRpcServer.createCallerFactory(router);

export type Router = typeof router;