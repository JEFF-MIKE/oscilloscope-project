<script lang="ts">
	import { page } from '$app/stores';
  import { trpc } from '$lib/trpc';
  import { mdiCheck, mdiAlertCircle } from "@mdi/js";
  import Button, { Label } from '@smui/button';
  import CircularProgress from '@smui/circular-progress';

  // We want to reset the scope, in order for it to be set to a known state
  let resetResponse = trpc($page).scopeGenericWriteHandler.mutate({ message: "*RST\n" });

  let scopeIdentity = trpc($page).scopeGenericQueryHandler.query({message: "*IDN?\n"});

  let scopeAcquireMode = trpc($page).scopeGenericQueryHandler.query({message: ":ACQUIRE:TYPE?\n"});

  const resetScope = async () => {
    resetResponse = trpc($page).scopeGenericWriteHandler.mutate({ message: "*RST\n" });

    scopeIdentity = trpc($page).scopeGenericQueryHandler.query({message: "*IDN?\n"});
    
    scopeAcquireMode = trpc($page).scopeGenericQueryHandler.query({message: ":ACQUIRE:TYPE?\n"});
  }
</script>

<div class="scope-launch-fetcher">
  <div class="status-list">
    <div class="status-row">
    {#if resetResponse}
      {#await resetResponse}
        <p>Resetting...</p>
        <CircularProgress style="width: 24px; height: 24px;" indeterminate />
      {:then response}
        <p>Reset response: <span class="success">{response}</span></p>
        <svg viewBox="0 0 24 24" fill="green" width="24" height="24">
          <path d={mdiCheck} />
        </svg>
      {:catch error}
        <p>Error resetting: <span class="error">{error.message}</span></p>
        <svg viewBox="0 0 24 24" fill="red" width="24" height="24">
          <path d={mdiAlertCircle} />
        </svg>
      {/await}
    {/if}
    </div>
    <div class="status-row">
    {#if scopeIdentity}
    {#await scopeIdentity}
        <p>Getting scope identity...</p>
        <CircularProgress style="width: 24px; height: 24px;" indeterminate />
      {:then response}
        <p>Scope identity: <span class="success">{response}</span></p>
        <svg viewBox="0 0 24 24" fill="green" width="24" height="24">
          <path d={mdiCheck} />
        </svg>
      {:catch error}
        <p>Error getting scope identity: <span class="error">{error.message}</span></p>
        <svg viewBox="0 0 24 24" fill="red" class="icon">
          <path d={mdiAlertCircle} />
        </svg>
      {/await}
    {/if}
    </div>
    <div class="status-row">
    {#if scopeAcquireMode}
      {#await scopeAcquireMode}
        <p>Getting scope acquire mode...</p>
        <CircularProgress style="width: 24px; height: 24px;" indeterminate />
      {:then response}
        <p>Scope acquire mode: <span class="success">{response}</span></p>
        <svg viewBox="0 0 24 24" fill="green" width="24" height="24">
          <path d={mdiCheck} />
        </svg>
      {:catch error}
        <p>Error getting scope acquire mode: <span class="error">{error.message}</span></p>
        <svg viewBox="0 0 24 24" fill="red" width="24" height="24">
          <path d={mdiAlertCircle} />
        </svg>
      {/await}
    {/if}
    </div>
  </div>
  <div class="button-class">
    <Button on:click={resetScope} variant="raised"><Label>Redo</Label></Button>
  </div>
</div>

<style>
  .error {
    color: red;
  }

  .success {
    color: green;
  }


  .status-list {
    display: flex;
    flex: 3;
    flex-direction: column;
    width: 100%;
  }

 .status-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
 }

 .icon {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 24px;
    width: 24px;
    margin-block-end: 1em;
    margin-block-start: 1em;
 }

 .scope-launch-fetcher {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 80%;
    margin-left: auto;
    margin-right: auto;
 }
 
 .button-class {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
 }
</style>

