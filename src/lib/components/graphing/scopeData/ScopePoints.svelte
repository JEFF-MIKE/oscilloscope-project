<script type="ts">
    import Slider from '@smui/slider';
    import Button, { Label } from '@smui/button';
    import { trpc } from '$lib/trpc';
    import { page } from '$app/stores';
	import ScopeStatus from './ScopeStatus.svelte';
    import { mdiAlert } from '@mdi/js';
    import Tooltip, { Wrapper } from '@smui/tooltip';
    let value = 100;
    let waveformPointsMode = trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS:MODE?\n"});
    let sliderValue = trpc($page).scopeGenericQueryHandler.query({message: ":WAVEFORM:POINTS?\n"});
    const waveformModes = ["Normal", "Maximum", "Raw"];
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
        <div class="waveform-status-wrapper">
            <ScopeStatus statusPromise={waveformPointsMode} statusLabel="Waveform Points Mode"/>
        </div>
        <div class="button-container">
            {#each waveformModes as mode}
                <Button on:click={() => setSliderMode(mode)} variant="raised"><Label>{mode}</Label></Button>
            {/each}
        </div>
    </div>
    <div class="waveform-points-container">
        <div class="waveform-mode-container">
            <div class="waveform-status-wrapper">
                <ScopeStatus statusPromise={sliderValue} statusLabel="Number of Points"/>
            </div>
            <div class="button-container single-button">
                <Button on:click={setSliderValue} variant="raised"><Label>Set number of points to {value}</Label></Button>
                {#if value > 20000}
                    <Wrapper>
                    <svg viewBox="0 0 24 24" fill="orange" width="24" height="24">
                        <path d={mdiAlert} />
                    </svg>
                    <Tooltip>Setting the number of points beyond 20000 may cause performance issues for the browser</Tooltip>
                    </Wrapper>
                {/if}
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

    .waveform-status-wrapper {
        flex: 3;
    }

    .button-container {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-evenly;
        align-items: center;
    }


    .slider {
        flex: 3;
    }

    .single-button {
        justify-content: space-around;
    }

    .waveform-mode-container, .waveform-points-container {
        display: flex;
        justify-content: space-between;
    }
    .waveform-points-container {
        flex-direction: column;
    }
</style>