<script>
    import { LayerCake, Svg, Html } from 'layercake';
  
    import Line from './Line.svelte';
    import AxisX from './AxisX.svelte';
    import AxisY from './AxisY.svelte';
    import Brush from './Brush.html.svelte';
  
    export let min = null;
    export let max = null;
    export let xKey = 'Time';
    export let yKey = 'Frequency';
    export let data = [];
    export let stroke = '#00e047';

    export let xLabel = "Time (s)";
    export let yLabel = "Frequency (Hz)";
  
    let brushedData;
    $: {
      brushedData = data.slice((min || 0) * data.length, (max || 1) * data.length);
      if (brushedData.length < 2) {
        brushedData = data.slice(min * data.length, min * data.length + 2);
      }
    }
  </script>
  
  <div class="chart-wrapper">
    <div class="chart-container">
      <LayerCake
        padding={{ bottom: 20, left: 25 }}
        x={xKey}
        y={yKey}
        data={brushedData}
      >
        <Svg>
          <AxisX
            ticks={ticks => {
              const filtered = ticks.filter(t => t % 1 === 0);
              if (filtered.length > 7) {
                return filtered.filter((t, i) => i % 2 === 0);
              }
              return filtered;
            }}
            label={xLabel}
          />
          <AxisY ticks={2} label={yLabel}/>
          <Line {stroke} />
        </Svg>
      </LayerCake>
    </div>
  
    <div class="brush-container">
      <LayerCake padding={{ top: 5 }} x={xKey} y={yKey} {data}>
        <Svg>
          <Line {stroke} />
        </Svg>
        <Html>
          <Brush bind:min bind:max />
        </Html>
      </LayerCake>
    </div>
  </div>
  
  <style>
    .chart-wrapper {
      width: 100%;
      height: 75%;
    }
    /*
      The wrapper div needs to have an explicit width and height in CSS.
      It can also be a flexbox child or CSS grid element.
      The point being it needs dimensions since the <LayerCake> element will
      expand to fill it.
    */
    .chart-container {
      width: 100%;
      height: 80%;
    }
    .brush-container {
      width: 100%;
      height: 20%;
    }
  </style>