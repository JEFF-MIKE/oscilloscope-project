import { initTRPC } from '@trpc/server'; 
import type { Context } from '$lib/server/context';
import { scopeAcquireGraphData, scopeGenericQueryHandler, scopeGenericWriteHandler } from './scopeFunctions/scopeFunctions';
import z from 'zod';

const tRpcServer = initTRPC.context<Context>().create();

const scopeInputSchema = z.object({
    message: z.string()
});


export const router = tRpcServer.router({
    example: tRpcServer.procedure.query(async ({ctx: {deviceSession, visaDriver }}) => {
        return `Hello from tRPC server: Your device session is: ${deviceSession} and your visa driver is: ${visaDriver}`;
    }),
    scopeGenericQueryHandler: tRpcServer.procedure.input(scopeInputSchema).query(async ({ ctx: { deviceSession }, input: { message } }) => {
        console.log(`Querying device with message: ${message}`);
        return scopeGenericQueryHandler(deviceSession, message);
    }),
    scopeGenericWriteHandler: tRpcServer.procedure.input(scopeInputSchema).mutation(async ({ ctx: { deviceSession }, input: { message } }) => {
        console.log(`Server: Writing to device with message: ${message}`);
        return scopeGenericWriteHandler(deviceSession, message);
    }),
    scopeAcquireGraphData: tRpcServer.procedure.query(async ({ ctx: { deviceSession } }) => {
        scopeAcquireGraphData(deviceSession);
    }),
});

export const createCaller = tRpcServer.createCallerFactory(router);

export type Router = typeof router;