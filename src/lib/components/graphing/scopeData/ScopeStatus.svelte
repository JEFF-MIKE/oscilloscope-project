<script lang="ts">
	import { mdiCheck, mdiAlertCircle } from "@mdi/js";
    import CircularProgress from "@smui/circular-progress";
    export let statusPromise: Promise<string> | null = null;
    export let statusLabel: string = "scope communication status:"
</script>

<div class="status-element">
    {#if statusPromise}
      {#await statusPromise}
        <p>Loading {statusLabel}...</p>
        <CircularProgress style="width: 24px; height: 24px;" indeterminate />
      {:then response}
        <p>{statusLabel} <span class="success-status">{response}</span></p>
        <svg viewBox="0 0 24 24" fill="green" width="24" height="24">
          <path d={mdiCheck} />
        </svg>
      {:catch error}
        <p>Error with {statusLabel}: <span class="error-status">{error.message}</span></p>
        <svg viewBox="0 0 24 24" fill="red" width="24" height="24">
          <path d={mdiAlertCircle} />
        </svg>
      {/await}
    {/if}
</div>

<style>
 .status-element {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
 }

 .error-status {
    color: red;
  }

  .success-status {
    color: green;
  }
</style>