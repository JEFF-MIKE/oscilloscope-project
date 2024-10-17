<script lang="ts">
	import { page } from '$app/stores';
  import { trpc } from '$lib/trpc';
  import ScopeStatus from './ScopeStatus.svelte';
  import Button, { Label } from '@smui/button';

  // We want to reset the scope, in order for it to be set to a known state
  let resetResponse = trpc($page).scopeGenericWriteHandler.mutate({ message: "*RST\n" });

  let scopeIdentity = trpc($page).scopeGenericQueryHandler.query({message: "*IDN?\n"});

  let scopeAcquireMode = trpc($page).scopeGenericQueryHandler.query({message: ":ACQUIRE:TYPE?\n"});

  let promiseList = [resetResponse, scopeIdentity, scopeAcquireMode];

  const messageDescriptions = [
    "Reset scope",
    "Scope identity",
    "Scope Acquire Mode",
]

  const resetScope = async () => {
    resetResponse = trpc($page).scopeGenericWriteHandler.mutate({ message: "*RST\n" });

    scopeIdentity = trpc($page).scopeGenericQueryHandler.query({message: "*IDN?\n"});
    
    scopeAcquireMode = trpc($page).scopeGenericQueryHandler.query({message: ":ACQUIRE:TYPE?\n"});

    // re-assign promiseList to get the new statuses
    promiseList = [resetResponse, scopeIdentity, scopeAcquireMode];
  }
</script>

<div class="scope-launch-fetcher">
  <div class="status-list">
    {#each promiseList as statusPromise, statusIndex}
      <ScopeStatus statusPromise={statusPromise} statusLabel={messageDescriptions[statusIndex]}/>
    {/each}
  </div>
  <div class="button-class">
    <Button on:click={resetScope} variant="raised"><Label>Redo</Label></Button>
  </div>
</div>

<style>
  .status-list {
    display: flex;
    flex: 3;
    flex-direction: column;
    width: 100%;
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

