// This file runs on the servers side, then sends it along to the client
import { getRandomNumber } from "$lib/server/randomNumber/randomNumber"
import type { GraphDataPoint } from "./graph_datatypes";
import * as NIVisa from 'node-ni-visa';
import { writeFileSync } from 'node:fs'
import path from 'path';

export function load(){

    // generateRandomizedSquareWave(1, 50),
    return {
        squareWave: generateRandomizedSquareWave(1, 100),
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

// const getGraphDataFromScope = () => {
//     // Page 744 of manual outlines a good session example.

    // Write a message to digitize the current capture data from the scope
    // try {
    //     const digitizeResponse = NIVisa.viWrite(deviceSession, ':DIGitize\n');
    //     console.log(`Digitize Response was: ${digitizeResponse}`);
    // } catch (error) {
    //     console.error(`Error writing to device: ${error}`);
    // }

//     // See what happens when we try to call the Display Query
//     try {
//         const displayQueryResponse = NIVisa.query(deviceSession, ":DISPLAY:DATA? PNG, SCReen, COLor\n", 100000);
//         console.log(`Display Query is: ${displayQueryResponse}, length of display query response is: ${displayQueryResponse.length}`,);
//         // dump contents to file
//         // first, build out filename via __dirname
//         const filePath = path.join(process.cwd(), 'display_data.png');
//         console.log(`Filepath is: ${filePath}`);
//         console.log(`Writing to file...`);
//         writeFileSync(filePath, displayQueryResponse);
//         console.log(`Wrote to file`);
//     } catch (error) {
//         console.error(`Error querying display data: ${error}`);
//     }
//     // Get the waveform preamble
//     const preamble = getWaveformPreamble(deviceSession);
//     console.log(`Preamble is: ${JSON.stringify(preamble, null, 4)}`);
//     // See what happens when we call the WAVEFORM:DATA? query

//     // Set up how many points to get with a write statement
//     scopeGenericWriteHandler(deviceSession, ":WAVEFORM:POINTS:MODE RAW\n");
//     const numPoints = 20000;
//     const numPointsHeaderLength = 10;

//     // Before acquiring the waveform data, we will want to execute the run and stop commands
//     scopeGenericWriteHandler(deviceSession, `:WAVEFORM:POINTS ${numPoints}\n`);
//     scopeGenericWriteHandler(deviceSession, ":RUN\n");
//     scopeGenericWriteHandler(deviceSession, ":STOP\n");
//     let waveformResponseData;
//     try {
//         const waveFormData = NIVisa.query(deviceSession, ":WAVEFORM:DATA?\n", numPoints + numPointsHeaderLength);
//         console.log(`Waveform Data is: ${waveFormData}`);
//         waveformResponseData = processWaveformData(waveFormData, preamble, numPoints);
//     } catch (error) {
//         console.error(`An error occured getting the waveform data: ${error}`);
//     }
//     // Close device communication session
//     NIVisa.viClose(deviceSession)

//     // Close NI-VISA driver
//     NIVisa.viClose(driverSession)
//     return waveformResponseData;
// }