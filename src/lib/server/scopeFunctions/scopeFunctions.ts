import * as NIVisa from 'node-ni-visa';

/**
 * Send a write message to the oscilloscope, including errors with a try/catch
 * 
 * @param deviceSession session number acquired from the VISA driver
 * @param message scope write message
 */
export const scopeGenericWriteHandler = (deviceSession: number, message: string) => {
    try {
        const responseLength = NIVisa.viWrite(deviceSession, message);
        if (responseLength === message.length) {
            console.log(`Server: Successfully wrote message ${message.replace(/\n/, '')} to Oscilloscope!`);
            return `Successfully wrote message ${message.replace(/\n/, '')} to Oscilloscope!`;
        } else {
            console.log(`Server: Message: ${message} was not written to device`);
            return `Length of message written was not the same as the message length`;
        }
    } catch (err) {
        console.error(`Server: Error when writing to device: ${err}`);
        return `An Error occured when writing to the device with command ${message}, error is: ${err}`;
    }
  };
  
  /**
   * Handle the query response from the oscilloscope, including errors with a try/catch
   * 
   * If you need to use the value from the query, use the NIVisa.query method directly
   * @param deviceSession session number acquired from the VISA driver
   * @param message scope query message
   */
  export const scopeGenericQueryHandler = (deviceSession: number, message: string) => {
    try {
        const response = NIVisa.query(deviceSession, message);
        console.log(`Query: ${message}: Sending response ${response} to client`);
        return response;
    } catch (err) {
        console.error(`Error querying device: ${err}`);
        return `An Error occured when querying the device with command ${message}, error is: ${err}`;
    }
  };

  /**
   * Perform a routine to acquire waveform data from the oscilloscope
   * 
   * Note: The user should use perform a write statement with :WAVEFORM:POINTS <number> before calling this function
   * 
   */
  export const scopeAcquireGraphData = (deviceSession: number) => {
    const digitizeResponse = NIVisa.viWrite(deviceSession, ':DIGitize\n');

    const currentNumPoints = NIVisa.query(deviceSession, ':WAVEFORM:POINTS?\n');
    const HEADER_LENGTH = 10; // represents #800... of response

    const waveformPreableData = NIVisa.query(deviceSession, ':WAVEFORM:PREAMBLE?\n');

    const processedWaveformData = processWaveformPreamble(waveformPreableData);

    const waveFormData = NIVisa.query(deviceSession, ':WAVEFORM:DATA?\n', Number(currentNumPoints.replace(/\n/, '')) + HEADER_LENGTH);

    const coordinates = processWaveformData(waveFormData, processedWaveformData, Number(currentNumPoints.replace(/\n/, '')));

    return coordinates;
  }


  const processWaveformPreamble = (waveformPreamble: string) => {
    // Call waveform preamble query
    // split out the preamble into its parts
    const preambleParts = waveformPreamble.split(',');
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
    // // Perform some calculations from the waveformPreambleData
    // const fVdiv = waveformPreambleData.yIncrement * 32;
    // const fOffset = waveformPreambleData.yOrigin;
    // const fSdiv = waveformPreambleData.points * waveformPreambleData.xIncrement / 10;
    // const fDelay = (waveformPreambleData.points / 2) * waveformPreambleData.xIncrement + waveformPreambleData.xOrigin;

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