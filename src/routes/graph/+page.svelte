<script lang="ts">
    import SyncedBrushWrapper from '$lib/components/graphing/SyncedBrushWrapper.svelte';
    import ScopeLaunchFetcher from '$lib/components/graphing/scopeData/ScopeLaunchFetcher.svelte';
	  import ScopePoints from '$lib/components/graphing/scopeData/ScopePoints.svelte';

    export let data;

    let brushExtents = [null, null];
    const xKey = "time_seconds";
    const yKey = "freq_hz";

    let tRpcLoading = false;

    const colors = ['#00e047'];
    // console.table(data.squareWave);

</script>

<h4 class="mdc-typography--headline4 ">Graph Page</h4>
<ScopeLaunchFetcher />
<div class="slider-container">
  <ScopePoints />
</div>
<div class="chart-container">
  <SyncedBrushWrapper
    data={data.squareWave}
    {xKey}
    {yKey}
    bind:min={brushExtents[0]}
    bind:max={brushExtents[1]}
    stroke={colors[0]}
  />
  <p color="white">X axis: time (s)</p>
  <p>Y axis: frequency (hz)</p>
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
      flex-wrap: wrap;
      justify-content: space-between;
      align-content: space-between;
      margin-left: 10%;
      margin-right: 10%;
    }
  </style>