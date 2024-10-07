import type { RequestEvent } from '@sveltejs/kit';

type TRPCContext = {
  // The NIVisa library currently does not have a discover device function. For now, declare the device via an environment variabl
    event: RequestEvent,
    deviceSession: Number | null,
}

export type Context = Awaited<TRPCContext>;