<script lang="ts">
  import { onMount } from "svelte";
  import Chart from 'chart.js/auto'

async function get_dataset(dataset: string): Promise<[Array<any>, Array<any>]> {
    let table = await fetch("/eugc/api/v1/datasets/" + dataset);
    let json = await table.json();
    return [json.xs, json.ys];
}
onMount(() => {
(async function() {
  let [xs, ys] = await get_dataset("signups");
  let [xs2, ys2] = await get_dataset("flights");
  new Chart(
    canvas,
    {
      type: 'line',
      data: {
        labels: xs,
        datasets: [
          {
            label: "signups",
            data: ys
          },
          {
            label: "flights",
            data: ys2
          }
        ]
      }
    }
  );
  let [xs3, ys3] = await get_dataset("signups_by_day");
  new Chart(
    canvas_day,
    {
      type: 'bar',
      data: {
        labels: xs3,
        datasets: [
          {
            label: "signups by day",
            data: ys3
          },
        ]
      }
    }
  );
  let [xs4, ys4] = await get_dataset("instructors");
  new Chart(canvas_instruct, {
      type: 'pie',
      data: {
        labels: xs4,
        datasets: [{label: "instructors", data: ys4}]
      }
    }
  );
  let [xs5, ys5] = await get_dataset("transporters");
  new Chart(canvas_transport, {
      type: 'pie',
      data: {
        labels: xs5,
        datasets: [{label: "transporters", data: ys5}]
      }
    }
  );
  let [xs6, ys6] = await get_dataset("supervisors");
  new Chart(canvas_supervise, {
      type: 'pie',
      data: {
        labels: xs6,
        datasets: [{label: "supervisors", data: ys6}]
      }
    }
  );
})();

});
 
let canvas: HTMLCanvasElement;
let canvas_day: HTMLCanvasElement;
let canvas_instruct: HTMLCanvasElement;
let canvas_transport: HTMLCanvasElement;
let canvas_supervise: HTMLCanvasElement;

 </script>

<div style="width: 800px;"><canvas id="per_week" bind:this={canvas}></canvas></div>
<div style="width: 800px;"><canvas id="per_day" bind:this={canvas_day}></canvas></div>
<div style="display: flex; flex-direction: row;">
  <div style=""><canvas id="instruct" bind:this={canvas_instruct}></canvas></div>
  <div style=""><canvas id="transport" bind:this={canvas_transport}></canvas></div>
  <div style=""><canvas id="supervise" bind:this={canvas_supervise}></canvas></div>
</div>
