<script lang="ts">
	import { page } from '$app/stores';
  import { trpc } from '$lib/trpc';

  // We want to reset the scope, in order for it to be set to a known state
  let resetResponse = trpc($page).scopeGenericWriteHandler.mutate({ message: "*RST\n" });

  let scopeIdentity = trpc($page).scopeGenericQueryHandler.query({message: "*IDN?\n"});

  let scopeAcquireMode = trpc($page).scopeGenericQueryHandler.query({message: ":ACQUIRE:TYPE?\n"});

</script>

<div>
  {#if resetResponse}
    {#await resetResponse}
      <p>Resetting...</p>
    {:then response}
      <p>Reset response: {response}</p>
    {:catch error}
      <p>Error resetting: {error.message}</p>
    {/await}
  {/if}
  {#if scopeIdentity}
   {#await scopeIdentity}
      <p>Getting scope identity...</p>
    {:then response}
      <p>Scope identity: {response}</p>
    {:catch error}
      <p>Error getting scope identity: {error.message}</p>
    {/await}
  {/if}
  {#if scopeAcquireMode}
    {#await scopeAcquireMode}
      <p>Getting scope acquire mode...</p>
    {:then response}
      <p>Scope acquire mode: {response}</p>
    {:catch error}
      <p>Error getting scope acquire mode: {error.message}</p>
    {/await}
  {/if}
</div>