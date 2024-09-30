// This file runs on the servers side, then sends it along to the client
import { getRandomNumber } from "$lib/server/randomNumber/randomNumber"
import type { GraphDataPoint } from "./graph_datatypes";
import * as NIVisa from 'node-ni-visa';
import { writeFileSync } from 'node:fs'
import path from 'path';

export function load(){

    // generateRandomizedSquareWave(1, 50),
    return {
        squareWave: getGraphDataFromScope(),
    }
}

const generateRandomizedSquareWave = (start_time: number, end_time: number) => {
    // For now, time is in seconds
    // high_freq and low_freq are in Hz
    // for every 1 second, determine whether to raise high, or drop voltage
    const square_wave_list: GraphDataPoint[] = [];
    for (let i = start_time; i < end_time; i++) {
        const random_freq = getRandomNumber(0, 2);
        // store the generated co-ordinate. We need to see if a rising edge or falling edge is required first.
        const generatedSqaureWaveCoord = {
            freq_hz: random_freq,
            time_seconds: i
        };
        if (random_freq === 0) {
            // this is a single co-ordinate, a straight line of 0 on the x axis.
            // a straight line is always required.
            if (square_wave_list.length === 0 || square_wave_list[square_wave_list.length - 1].freq_hz === 0) {
                square_wave_list.push(generatedSqaureWaveCoord);
                continue
            } else {
                // Previous freq_hz was one. this means this co-ordinate is a falling edge, and needs another co-ordinate to
                // represent the dropdown.
                square_wave_list.push({
                    freq_hz: 1,
                    time_seconds: i
                });
                square_wave_list.push(generatedSqaureWaveCoord);
            }
        } else {
            // random frequency is 1
            if (square_wave_list.length === 0 || square_wave_list[square_wave_list.length - 1].freq_hz === 1) {
                square_wave_list.push(generatedSqaureWaveCoord);
                continue;
            } else {
                // Previous freq_hz was 0. this means this co-ordinate is a rising edge, and needs another co-ordinate to
                // represent the rise.
                square_wave_list.push({
                    freq_hz: 0,
                    time_seconds: i})
                }
                square_wave_list.push(generatedSqaureWaveCoord);
        }
    }
    return square_wave_list;
}

const getGraphDataFromScope = () => {
    // Page 744 of manual outlines a good session example.
    const driverSession = NIVisa.viOpenDefaultRM();

    console.log(`Driver session: ${driverSession}`);

    const deviceSession = NIVisa.viOpen(driverSession, "USB0::0x0957::0x1763::MY50070186::INSTR");

    console.log(`Device session: ${deviceSession}`);

    // When working with the scope, we want to make sure it is reset. This puts it in a known state
    scopeGenericWriteHandler(deviceSession, "*RST\n");

    // Query the device for a message.
    scopeGenericQueryHandler(deviceSession, "*IDN?\n");
    
    // Set the acquire mode to normal
    scopeGenericWriteHandler(deviceSession, ":ACQUIRE:TYPE NORMal\n");

    // Query about the current acquire mode
    scopeGenericQueryHandler(deviceSession, ":ACQUIRE:TYPE?\n");

    // Learn about the device details
    try {
        const learnCommandResponse = NIVisa.query(deviceSession, '*LRN?\n');
        console.log(`Learn command response is: ${learnCommandResponse}`);
    } catch(error) {
        console.log(`Error learning about device: ${error}`);
    }

    // Note: the "*TST?\n" command seems to always return an error, so comment it out for now
    // scopeGenericQueryHandler(deviceSession, '*TST?\n');

    // // Write a message to digitize the current capture data from the scope
    // try {
    //     const digitizeResponse = NIVisa.viWrite(deviceSession, ':DIGitize\n');
    //     console.log(`Digitize Response was: ${digitizeResponse}`);
    // } catch (error) {
    //     console.error(`Error writing to device: ${error}`);
    // }

    // See what happens when we try to call the Display Query
    try {
        const displayQueryResponse = NIVisa.query(deviceSession, ":DISPLAY:DATA? PNG, SCReen, COLor\n", 100000);
        console.log(`Display Query is: ${displayQueryResponse}, length of display query response is: ${displayQueryResponse.length}`,);
        // dump contents to file
        // first, build out filename via __dirname
        const filePath = path.join(process.cwd(), 'display_data.png');
        console.log(`Filepath is: ${filePath}`);
        console.log(`Writing to file...`);
        writeFileSync(filePath, displayQueryResponse);
        console.log(`Wrote to file`);
    } catch (error) {
        console.error(`Error querying display data: ${error}`);
    }
    // Get the waveform preamble
    const preamble = getWaveformPreamble(deviceSession);
    console.log(`Preamble is: ${JSON.stringify(preamble, null, 4)}`);
    // See what happens when we call the WAVEFORM:DATA? query

    // Set up how many points to get with a write statement
    scopeGenericWriteHandler(deviceSession, ":WAVEFORM:POINTS:MODE RAW\n");
    const numPoints = 20000;
    const numPointsHeaderLength = 10;

    // Before acquiring the waveform data, we will want to execute the run and stop commands
    scopeGenericWriteHandler(deviceSession, `:WAVEFORM:POINTS ${numPoints}\n`);
    scopeGenericWriteHandler(deviceSession, ":RUN\n");
    scopeGenericWriteHandler(deviceSession, ":STOP\n");
    let waveformResponseData;
    try {
        const waveFormData = NIVisa.query(deviceSession, ":WAVEFORM:DATA?\n", numPoints + numPointsHeaderLength);
        console.log(`Waveform Data is: ${waveFormData}`);
        waveformResponseData = processWaveformData(waveFormData, preamble, numPoints);
    } catch (error) {
        console.error(`An error occured getting the waveform data: ${error}`);
    }
    // Close device communication session
    NIVisa.viClose(deviceSession)

    // Close NI-VISA driver
    NIVisa.viClose(driverSession)
    return waveformResponseData;
}

enum WaveformFormat {
    BYTE,
    WORD,
    ASCII
}

enum WaveformType {
    NORMAL,
    PEAK_DETECT,
    AVERAGE,
}

interface PreambleObject {
    format: WaveformFormat,
    type: WaveformType,
    points: number,
    count: number, // always 1
    xIncrement: number,
    xOrigin: number,
    xReference: number,
    yIncrement: number,
    yOrigin: number,
    yReference: number,
};

const getWaveformPreamble = (deviceSession: number) => {
    // Call waveform preamble query
    const waveFormPreamble = NIVisa.query(deviceSession, ":WAVEFORM:PREAMBLE?\n");
    // split out the preamble into its parts
    const preambleParts = waveFormPreamble.split(',');
    // create the preamble object
    return {
        format: parseInt(preambleParts[0]),
        type: parseInt(preambleParts[1]),
        points: parseInt(preambleParts[2]),
        count: parseInt(preambleParts[3]),
        xIncrement: parseFloat(preambleParts[4]),
        xOrigin: parseFloat(preambleParts[5]),
        xReference: parseInt(preambleParts[6]),
        yIncrement: parseFloat(preambleParts[7]),
        yOrigin: parseFloat(preambleParts[8]),
        yReference: parseInt(preambleParts[9]),
    }
};

const processWaveformData = (waveformByteData: string, waveformPreambleData: PreambleObject, numPoints: number) => {
    // deal with the waveformByteData first!
    const waveformData = waveformByteData.split('');
    const headerLength = 10;
    // The first 10 bytes are the header, so we can skip those
    // We want to build a number from indexes 1 to 10 (inclusive)
    const waveformHeaderLength = Number(waveformData.slice(2, 10).join(''));
    console.log(`Waveform Header is: ${waveformHeaderLength}`);
    // Perform some calculations from the waveformPreambleData
    const fVdiv = waveformPreambleData.yIncrement * 32;
    const fOffset = waveformPreambleData.yOrigin;
    const fSdiv = waveformPreambleData.points * waveformPreambleData.xIncrement / 10;
    const fDelay = (waveformPreambleData.points / 2) * waveformPreambleData.xIncrement + waveformPreambleData.xOrigin;

    // Start to loop through the waveform data, calculating the voltage
    // and the seconds.
    // Put the string into a buffer
    const headerStartIndex = 10;
    const bufferHolder = Buffer.from(waveformData.slice(headerStartIndex + 1, numPoints).join(''));
    console.log(`BufferHolder is: ${bufferHolder}`);
    const coordinateHolder = [];
    for (let targetIndex = headerStartIndex; targetIndex < waveformByteData.length; targetIndex++) {
        // voltage is Y, seconds is X
        // console.log(`raw waveformData is: ${bufferHolder[targetIndex]}`);
        // console.log(`waveformData is: ${Number(bufferHolder[targetIndex])}`);
        const voltage = (Number(bufferHolder[targetIndex]) - waveformPreambleData.yReference) * waveformPreambleData.yIncrement + waveformPreambleData.yOrigin;
        const seconds = (targetIndex - waveformPreambleData.xReference) * waveformPreambleData.xIncrement + waveformPreambleData.xOrigin;
        coordinateHolder.push({
            time_seconds: seconds,
            freq_hz: voltage
        });
        // console.log(`For point ${targetIndex}, Voltage is: ${voltage}, Seconds is: ${seconds}`);
    }
    return coordinateHolder;
}

/**
 * Handle the query response from the oscilloscope, including errors with a try/catch
 * 
 * If you need to use the value from the query, use the NIVisa.query method directly
 * @param deviceSession session number acquired from the VISA driver
 * @param message scope query message
 */
const scopeGenericQueryHandler = (deviceSession: number, message: string) => {
    try {
        NIVisa.query(deviceSession, message);
    } catch (err) {
        console.error(`Error querying device: ${err}`);
    }
};

/**
 * Send a write message to the oscilloscope, including errors with a try/catch
 * 
 * @param deviceSession session number acquired from the VISA driver
 * @param message scope write message
 */
const scopeGenericWriteHandler = (deviceSession: number, message: string) => {
    try {
        const responseLength = NIVisa.viWrite(deviceSession, message);
        if (responseLength === message.length) {
            console.log(`Successfully wrote message ${message.replace(/\n/, '')} to Oscilloscope!`);
        } else {
            throw new Error(`Length of message written was not the same as the message length`);
        }
    } catch (err) {
        console.error(`Error writing to device: ${err}`);
    }
};