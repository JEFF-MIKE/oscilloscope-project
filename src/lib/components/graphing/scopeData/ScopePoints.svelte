<script type="ts">
    import Slider from '@smui/slider';
    import Button, { Label } from '@smui/button';
    import { trpc } from '$lib/trpc';
    import { page } from '$app/stores';
    let value = 100;
    let waveformPointsMode = trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS:MODE?\n"});
    let sliderValue = trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS?\n"});
    const setSliderValue = async() => {
        try {
            console.log(`Value is: ${value}`);
            const response = await trpc($page).scopeGenericWriteHandler.mutate({message: `:WAVEFORM:POINTS ${value}\n`});
            console.log(`Client: Response from server:${response.replace(/\n/, "")}`);
            sliderValue = trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS?\n"});
        } catch (error) {
            console.error(error);
        }
    }

    const setSliderMode = async(mode) => {
        try {
            console.log(`mode is: ${JSON.stringify(mode)}`);
            const response = await trpc($page).scopeGenericWriteHandler.mutate({message: `:WAVEFORM:POINTS:MODE ${mode}\n`});
            console.log(`Client: Response from server:${response.replace(/\n/, "")}`);
            waveformPointsMode = trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS:MODE?\n"});
        } catch(err) {
            console.log(err);
        }
    }

</script>

<div class="slider-wrapper">
    <div class="waveform-mode-container">
        <div class="waveform-status-action">
        {#await waveformPointsMode}
            <p>Getting waveform points mode... </p>
        {:then pointsMode}
            <p>Waveform Points Mode: {pointsMode}</p>
        {:catch error}
            <p>Error getting waveform points mode: <span class="error">{error.message}</span></p>
        {/await}
        </div>
        <div class="button-container">
            <Button variant="raised" on:click={() => setSliderMode("Normal")}><Label>Normal</Label></Button>
            <Button variant="raised" on:click={() => setSliderMode("Maximum")}><Label>Maximum</Label></Button>
            <Button variant="raised" on:click={() => setSliderMode("Raw")}><Label>Raw</Label></Button>
        </div>
    </div>
    <div class="waveform-points-container">
        <div class="waveform-mode-container">
            <div class="waveform-status-action">
            {#await sliderValue}
                <p>Getting number of points...</p>
            {:then scopePoints}
                <p>Current Number of Points on Scope: {scopePoints}</p>
            {:catch error}
                <p class="error">Error getting number of points: {error.message}</p>
            {/await}
            </div>
            <div class="button-container single-button">
                <Button on:click={setSliderValue} variant="raised"><Label>Set number of points to {value}</Label></Button>
            </div>
        </div>
        <div class="slider">
            <Slider bind:value min={100} max={80000} step={100} discrete/>
        </div>
    </div>
</div>

<style>
    .slider-wrapper {
    width: 80%;
    margin-left: auto;
    margin-right: auto;
    display: flex;
    flex-direction: column;
    }

    .waveform-status-action {
        flex: 3;
    }

    .button-container {
        flex: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .single-button {
        justify-content: center;
    }

    .slider {
        flex: 3;
    }

    .waveform-mode-container, .waveform-points-container, .waveform-status-action {
        display: flex;
        justify-content: space-between;
    }
    .waveform-points-container {
        flex-direction: column;
    }
</style>