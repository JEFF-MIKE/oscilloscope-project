export const sessionList: number[] = [];
export let driverSession: number; // driver is singleton
import * as NIVisa from 'node-ni-visa';
import { DEVICE_ADDRESS } from '$env/static/private';

export const createNewSession = () => {
    if (driverSession === undefined) {
        // assign driverSession to new value
        try {
            driverSession = NIVisa.viOpenDefaultRM();
        } catch (err) {
            throw new Error(`Error opening VISA driver for device session`);
        }
    }
    try {
        const newSession = NIVisa.viOpen(driverSession, DEVICE_ADDRESS);
        sessionList.push(newSession);
    } catch (err) {
        throw new Error(`Could not create a new Device session: ${err}`);
    }
}