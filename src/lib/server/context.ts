import type { RequestEvent } from '@sveltejs/kit';
import * as NIVisa from 'node-ni-visa';
import { DEVICE_ADDRESS } from '$env/static/private';

// below should be error handled.
const visaDriver = NIVisa.viOpenDefaultRM();
console.log(`Device Address is: ${DEVICE_ADDRESS}`);
const deviceSession = NIVisa.viOpen(visaDriver, DEVICE_ADDRESS);

export async function createContext(event: RequestEvent) {
  //
  console.log(`Connecting to VISA device with ${DEVICE_ADDRESS}`);
  // The NIVisa library currently does not have a discover device function. For now, declare the device via an environment variable
  return {
    event,
    visaDriver,
    deviceSession
  };
}

export type Context = Awaited<ReturnType<typeof createContext>>;