<script>
  import CardSection from './CardSection.svelte'
  import Spinner from 'svelte-spinner'
  import cn from 'classnames'
  import axios from 'axios'

  export let qrData = {}

  let states = {
    IDLE: 0,
    TIMING: 1,
    WRONGTIME: 2,
    QUERY: 3,
    FAILQUERY: 4,
    SUCCESS: 5,
  }

  let queryMessage = ''
  let state = states.IDLE

  async function start() {
    state = states.TIMING

    const valid = await verifyTimestamps()
    if (!valid) {
      state = states.WRONGTIME
    } else {
      state = states.QUERY
      queryData()
    }
  }

  const sleep = milliseconds => {
    return new Promise(resolve => setTimeout(resolve, milliseconds))
  }

  async function verifyTimestamps() {
    let valid = true

    for (let i = 0; i < 10; i++) {
      const { timestamp } = qrData
      if (!timestamp) valid = false

      const current = new Date().getTime()
      const diff = Math.abs(current - +timestamp)
      valid &= diff < 150
      await sleep(100)
    }

    return valid
  }

  async function queryData() {
    axios
      .post(process.env.api, {
        otp: '' + qrData.otp,
        resourceId: qrData.stringId,
      })
      .then(res => {
        queryMessage = res.data
        state = states.SUCCESS
      })
      .catch(err => {
        if (err.response.status === 401) {
          queryMessage = 'Invalid OTP'
        } else {
          queryMessage = 'Resource does not exist'
        }
        state = states.FAILQUERY
      })
  }
</script>

<CardSection>
  <h2 class="text-2xl font-bold text-indigo-600">Scanner (Mock)</h2>
  <p class="text-lg">
    Usually this would happen on another device. But for the demo's sake, we're
    just doing it here.
  </p>
  <div class="h-6" />
  <button
    class="px-3 py-1 bg-indigo-600 border-none font-medium text-lg text-white
    shadow-sm rounded-sm"
    on:click={start}>
    Start Scan
  </button>
  <div class="h-4" />

  <div class={cn({ 'opacity-50': state < 1 })}>
    <p class="uppercase tracking-wide font-bold ">
      1. Verify One Second of Timestamps
    </p>
    {#if state === states.TIMING}
      <Spinner size="25" />
    {:else if state === states.WRONGTIME}
      <p class="text-red-600 flex items-center py-1">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          class="text-red-400 mr-2"
          xmlns="http://www.w3.org/2000/svg">
          <path
            d="M12 6C12.5523 6 13 6.44772 13 7V13C13 13.5523 12.5523 14 12
            14C11.4477 14 11 13.5523 11 13V7C11 6.44772 11.4477 6 12 6Z"
            fill="currentColor" />
          <path
            d="M12 16C11.4477 16 11 16.4477 11 17C11 17.5523 11.4477 18 12
            18C12.5523 18 13 17.5523 13 17C13 16.4477 12.5523 16 12 16Z"
            fill="currentColor" />
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228
            22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM4 12C4 16.4183
            7.58172 20 12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12
            4C7.58172 4 4 7.58172 4 12Z"
            fill="currentColor" />
        </svg>
        Code is Out of Date
      </p>
    {:else if state > states.WRONGTIME}
      <p class="text-green-600 flex items-center py-1">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          class="text-green-400 mr-2"
          xmlns="http://www.w3.org/2000/svg">
          <path d="M15 6H3V8H15V6Z" fill="currentColor" />
          <path d="M15 10H3V12H15V10Z" fill="currentColor" />
          <path d="M3 14H11V16H3V14Z" fill="currentColor" />
          <path
            d="M11.9905 15.025L13.4049 13.6106L15.526 15.7321L19.7687
            11.4895L21.1829 12.9037L15.526 18.5606L11.9905 15.025Z"
            fill="currentColor" />
        </svg>
        Code is Realtime
      </p>
    {/if}
  </div>

  <div class={cn({ 'opacity-50': state < 3 })}>
    <p class="uppercase tracking-wide font-bold ">
      2. Verify OTP and Resource ID on Server
    </p>
    {#if state === states.QUERY}
      <Spinner size="25" />
    {:else if state === states.FAILQUERY}
      <p class="text-red-600 flex items-center py-1">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          class="text-red-400 mr-2"
          xmlns="http://www.w3.org/2000/svg">
          <path
            d="M12 6C12.5523 6 13 6.44772 13 7V13C13 13.5523 12.5523 14 12
            14C11.4477 14 11 13.5523 11 13V7C11 6.44772 11.4477 6 12 6Z"
            fill="currentColor" />
          <path
            d="M12 16C11.4477 16 11 16.4477 11 17C11 17.5523 11.4477 18 12
            18C12.5523 18 13 17.5523 13 17C13 16.4477 12.5523 16 12 16Z"
            fill="currentColor" />
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228
            22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM4 12C4 16.4183
            7.58172 20 12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12
            4C7.58172 4 4 7.58172 4 12Z"
            fill="currentColor" />
        </svg>
        {queryMessage}
      </p>
    {:else if state === states.SUCCESS}
      <div class="text-green-600 flex items-center py-1">
        <pre>
          <code>{JSON.stringify(queryMessage, null, 2)}</code>
        </pre>
      </div>
    {/if}
  </div>
</CardSection>
