<script lang="ts">
	import { goto } from '$app/navigation';
    import Button, { Label } from '@smui/button';
    import TopAppBar, {Row, Section } from "@smui/top-app-bar"
</script>

<div>
    <TopAppBar variant="static">
        <Row>
            <Section>
                <Button color="secondary" href="/">Home</Button>
                <Button color="secondary" href="/graph"><Label>Graph</Label></Button>
                <Button color="secondary" href="/commands"><Label>Commands</Label></Button>
            </Section>
        </Row>
    </TopAppBar>
</div>

<slot></slot>