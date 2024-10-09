<script lang="ts">
    import SyncedBrushWrapper from '$lib/components/graphing/SyncedBrushWrapper.svelte';
    import ScopeLaunchFetcher from '$lib/components/graphing/scopeData/ScopeLaunchFetcher.svelte';
	  import ScopePoints from '$lib/components/graphing/scopeData/ScopePoints.svelte';
    import { trpc } from '$lib/trpc';
    import { page } from '$app/stores';
    import type { GraphDataPoint } from '$lib/types/GraphTypes';
    import Tab, { Label as TabLabel } from '@smui/tab';
    import TabBar from '@smui/tab-bar';
    import Button, { Label } from '@smui/button';
    import LinearProgress from '@smui/linear-progress'

    // get data points from the server.
    let graphData: null | Promise<GraphDataPoint[]> = null;

    let randomizedDummyWaveformData: null | Promise<GraphDataPoint[]> = null;

    let active = "Live Data";

    const getLiveGraphPoints = async () => {
      graphData = trpc($page).scopeAcquireGraphData.query();
    }

    const getRandomizedGraphDataPoints = async () => {
      randomizedDummyWaveformData = trpc($page).randomizedWaveformData.query();
    }

    const resetRandomizedDummyWaveformData = () => {
      randomizedDummyWaveformData = null
    };

    const clearAcquiredGraphData = () => {
      graphData = null;
    }

    let brushExtents = [null, null];
    const xKey = "time_seconds";
    const yKey = "freq_hz";


    const colors = ['#00e047'];
    // console.table(data.squareWave);

</script>

<h4 class="mdc-typography--headline4 header">Graph Page</h4>
<ScopeLaunchFetcher />
<div class="slider-container">
  <ScopePoints />
</div>
<div class="chart-container">
  <div class="tab-container">
    <TabBar tabs={['Live Data', 'Sample Data']} let:tab bind:active>
      <Tab {tab}>
        <TabLabel>
          {tab}
        </TabLabel>
      </Tab>
    </TabBar>
  </div>
    {#if active === "Live Data"}
      {#if !graphData}
        <div class="custom-button">
          <p>Press the button to get the graphData</p>
          <Button on:click={getLiveGraphPoints} color="primary" variant="raised">
            <Label>Get Waveform Data</Label>
          </Button>
        </div>
      {:else}
        {#await graphData}
        <div class="custom-button">
          <p>Fetching Data Points from Oscilloscope...</p>
          <LinearProgress indeterminate />
        </div>
        {:then graphData}
        <SyncedBrushWrapper
        data={graphData}
        {xKey}
        {yKey}
        bind:min={brushExtents[0]}
        bind:max={brushExtents[1]}
        stroke={colors[0]}
        />
        <div class="graph-button-instructions">
          <Button on:click={getLiveGraphPoints} color="primary" variant="raised">
            <Label>Refetch Waveform Data</Label>
          </Button>
          <Button on:click={clearAcquiredGraphData} color="primary" variant="raised">
            <Label>Clear Acquired Data</Label>
          </Button>
        </div>
        {:catch error}
          <p class="error-text custom-button">An error occured! {error}</p>
        {/await}
      {/if}
      {:else if active === "Sample Data"}
      {#if !randomizedDummyWaveformData}
        <div class="custom-button">
          <p>Press the button to generate randomized dummy data</p>
          <Button on:click={getRandomizedGraphDataPoints} color="primary" variant="raised">
            <Label>Generate Randomized Data</Label>
          </Button>
        </div>
      {:else}
        {#await randomizedDummyWaveformData}
          <p>
            <LinearProgress indeterminate />
          </p>
        {:then randomizedDummyWaveformData}
        <SyncedBrushWrapper
        data={randomizedDummyWaveformData}
        {xKey}
        {yKey}
        bind:min={brushExtents[0]}
        bind:max={brushExtents[1]}
        stroke={colors[0]}
        />
        <div class="graph-button-instructions">
          <Button on:click={getRandomizedGraphDataPoints} color="primary" variant="raised">
            <Label>Regenerate Dummy Waveform Data</Label>
          </Button>
          <Button on:click={resetRandomizedDummyWaveformData} color="primary" variant="raised">
            <Label>Clear Dummy Waveform Data</Label>
          </Button>
        </div>
          {:catch error}
            <p>An error occured! {error}</p>
          {/await}
      {/if}
    {/if}
</div>

<style>
    /*
      The wrapper div needs to have an explicit width and height in CSS.
      It can also be a flexbox child or CSS grid element.
      The point being it needs dimensions since the <LayerCake> element will
      expand to fill it.
    */
    .chart-container {
      width: 80%;
      height: 500px;
      display: flex;
      flex-direction: column;
      margin-left: 10%;
      margin-right: 10%;
    }

    .header {
      margin-left: 10%;
      margin-right: 10%;
      margin-top: 25px;
      margin-bottom: 25px;
    }

    .slider-container {
      margin-top: 10px;
      margin-bottom: 10px;
    }

    .custom-button {
      width: 100%;
      
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      margin: auto;
    }

    .error-text {
      color: red;
    }

    .tab-container {
      margin-bottom: 25px;
    }

    .graph-button-instructions {
      margin-bottom: 5px;
      margin-top: 20px;
      display: flex;
      justify-content: space-evenly;
    }
  </style>