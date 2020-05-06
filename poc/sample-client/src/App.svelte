<script>
  import Tailwindcss from './Tailwindcss.svelte'
  import Qr from './Qr.svelte'
  import CardSection from './CardSection.svelte'
  import Spinner from 'svelte-spinner'
  import Scanner from './Scanner.svelte'

  import cn from 'classnames'

  let paused = false
  let delay = 0
  let secret = 'HJWFMM2BOVAUSQTGNFBHCLDZKJ2G6TCDKIYV45CVOVUG4WDBKVRA'

  let qrData = {}

  const secrets = [
    'HJWFMM2BOVAUSQTGNFBHCLDZKJ2G6TCDKIYV45CVOVUG4WDBKVRA',
    '[Wrong] 2fd4e1c67a2d28fced849ee1bb76e7391b93eb12',
    // 'de9f2c7fd25e1b3afad3e85a0bd17d9b100db4b3',
  ]

  let selected = 0
  const resources = [
    {
      id: '3372bb97-4086-4760-a6da-61c7eafe9c06',
      name: 'Sick Kanye Tickets',
    },
    {
      name: 'Home Healthcare Check-in',
      id: 'bdf037c2-cbea-449c-bb7c-e1026906b13c',
    },
    {
      name: 'Broken, Fake resource',
      id: 'bdd037c2-cbea-449c-bb7c-e1026906b13c',
    },
  ]
</script>

<style>
  :global(html, body) {
    @apply leading-relaxed;
  }
</style>

<div class="container mx-auto max-w-2xl py-24">
  <div class="pr-4 ">
    <h1 class="text-3xl font-bold flex items-center ">
      <svg
        width="36"
        height="36"
        viewBox="0 0 24 24"
        fill="none"
        class="text-gray-700 mr-4"
        xmlns="http://www.w3.org/2000/svg">
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M9 3H3V9H5V5H9V3ZM3 21V15H5V19H9V21H3ZM15 3V5H19V9H21V3H15ZM19
          15H21V21H15V19H19V15ZM7 7H11V11H7V7ZM7 13H11V17H7V13ZM17
          7H13V11H17V7ZM13 13H17V17H13V13Z"
          fill="currentColor" />
      </svg>
      DinoQR Demo
    </h1>

    <p class="text-lg leading-relaxed mt-4">
      DinoQR is a project to create a time-secured, ultra-strong scannable code
      protocol. This enables uses from stopping scalpers at live events to
      ensuring that home healthcare providers actually visit their patients.
      We've built a demo generator and scanner as a proof of concept for the
      protcol.
    </p>

    <div class="h-12 " />

    <CardSection>
      <h2 class="text-2xl font-bold text-indigo-600">Generator</h2>
      <div class="h-6" />

      <div class="block mb-4">
        <span class="text-gray-700 mb-2">Demo</span>
        <div class="space-y-3">
          {#each resources as resource, i}
            <button
              class={cn(
                'p-2 bg-white w-full border-none appearance-none bg-gray-100 text-left active:shadow-none transition-all duration-75',
                {
                  'bg-indigo-100 text-indigo-900 shadow-none': i === selected,
                },
              )}
              on:click={() => (selected = i)}>
              <p class="text-lg font-bold">{resource.name}</p>
              <code class="text-xs text-gray-600 break-all">{resource.id}</code>
            </button>
          {/each}
        </div>
      </div>

      <label class="block">
        <span class="text-gray-700">Timestamp Delay (MS)</span>
        <input
          class="form-input mt-1 block w-full"
          bind:value={delay}
          placeholder="0" />
      </label>

      <div class="h-6" />

      <div class="block">
        <span class="text-gray-700">One Time Password Secret</span>
        <select class="form-select mt-1 block w-full" bind:value={secret}>
          {#each secrets as secret}
            <option value={secret}>{secret}</option>
          {/each}
        </select>
      </div>

      <div class="flex mt-6">
        <label class="flex items-center">
          <input type="checkbox" class="form-checkbox" bind:checked={paused} />
          <span class="ml-2">Pause Generation</span>
        </label>
      </div>

    </CardSection>
    <svg
      width="42"
      height="42"
      viewBox="0 0 24 24"
      fill="none"
      class="mx-auto text-gray-400 my-6"
      xmlns="http://www.w3.org/2000/svg">
      <path
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M10.9991 6.84976C9.83339 6.43819 8.99813 5.32671 8.99813
        4.02014C8.99813 2.36329 10.3413 1.02014 11.9981 1.02014C13.655 1.02014
        14.9981 2.36329 14.9981 4.02014C14.9981 5.32601 14.1638 6.43701 12.9991
        6.84911L13.0121 19.1375L14.8244 17.315L16.2426 18.7253L12.0119
        22.9799L7.75739 18.7491L9.16763 17.3309L11.0122 19.1652L10.9991
        6.84976ZM11.9981 5.02014C11.4458 5.02014 10.9981 4.57243 10.9981
        4.02014C10.9981 3.46786 11.4458 3.02014 11.9981 3.02014C12.5504 3.02014
        12.9981 3.46786 12.9981 4.02014C12.9981 4.57243 12.5504 5.02014 11.9981
        5.02014Z"
        fill="currentColor" />
    </svg>

    <Qr
      live={!paused}
      {delay}
      {secret}
      on:scan={e => (qrData = e.detail)}
      resourceId={resources[selected].id} />

    <svg
      width="42"
      height="42"
      viewBox="0 0 24 24"
      fill="none"
      class="mx-auto text-gray-400 my-6"
      xmlns="http://www.w3.org/2000/svg">
      <path
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M10.9991 6.84976C9.83339 6.43819 8.99813 5.32671 8.99813
        4.02014C8.99813 2.36329 10.3413 1.02014 11.9981 1.02014C13.655 1.02014
        14.9981 2.36329 14.9981 4.02014C14.9981 5.32601 14.1638 6.43701 12.9991
        6.84911L13.0121 19.1375L14.8244 17.315L16.2426 18.7253L12.0119
        22.9799L7.75739 18.7491L9.16763 17.3309L11.0122 19.1652L10.9991
        6.84976ZM11.9981 5.02014C11.4458 5.02014 10.9981 4.57243 10.9981
        4.02014C10.9981 3.46786 11.4458 3.02014 11.9981 3.02014C12.5504 3.02014
        12.9981 3.46786 12.9981 4.02014C12.9981 4.57243 12.5504 5.02014 11.9981
        5.02014Z"
        fill="currentColor" />
    </svg>

    <Scanner {qrData} />

  </div>
  <Tailwindcss />

</div>
