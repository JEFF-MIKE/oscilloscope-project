<script type="ts">
    import Slider from '@smui/slider';
    import Button, { Label } from '@smui/button';
    import { trpc } from '$lib/trpc';
    import { page } from '$app/stores';
    let value = 100;
    let scopePointsValue = 0;
    
    // TODO: make this part an enum
    let waveformPointsMode = "Unknown";

    // note: TRPC should have better responses
    const getSliderValue = async () => {
        try {
            const response = await trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS?\n"});
            scopePointsValue= Number(response.replace(/\n/, ""));
            console.log(`Points are: ${scopePointsValue}`);
        } catch (error) {
            console.error(error);
        }
    }

    const getWaveformPointsMode = async () => {
        try {
            const response = await trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS?\n"});
            waveformPointsMode = response.replace(/\n/, "");
        } catch (error) {
            console.error(error);
        }
    }

    
    const setSliderValue = async() => {
        try {
            console.log(`Value is: ${value}`);
            const response = await trpc($page).scopeGenericWriteHandler.mutate({message: `:WAVEFORM:POINTS ${value}\n`});
            console.log(`Client: Response from server:${response.replace(/\n/, "")}`);
            // Since this is successful here, set the previous scopePointsValue to the newly set value
            scopePointsValue = value;
        } catch (error) {
            console.error(error);
        }
    }
</script>

<div>
    {#await getSliderValue()}
        <p>Getting number of points...</p>
    {:then _}
        <p>Current Number of Points on Scope: {scopePointsValue}</p>
    {:catch error}
        <p>Error getting number of points: {error.message}</p>
    {/await}

    {#await getWaveformPointsMode()}
        <p>Waveform Points Mode: {waveformPointsMode}</p>
    {:catch error}
        <p>Error getting waveform points mode: {error.message}</p>
    {/await}

    <Slider bind:value min={100} max={80000} step={100} discrete/>
    <Button on:click={setSliderValue} variant="raised"><Label>Set number of points to {value}</Label></Button>
</div>