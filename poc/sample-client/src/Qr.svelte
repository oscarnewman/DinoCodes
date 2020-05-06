<script>
  import qrcode from 'qrcode/build/qrcode'
  import uuidParse from 'uuid-parse'
  //   import totp from 'totp-generator'
  import otplib from '@otplib/preset-browser'
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  export let resourceId = '15323'
  export let live = true
  export let delay = 0
  export let secret = 'HJWFMM2BOVAUSQTGNFBHCLDZKJ2G6TCDKIYV45CVOVUG4WDBKVRA'

  let img = ''
  let data = ''

  let curMs = new Date().getTime()
  $: data = intFromBytes(uuidParse.parse(resourceId))

  $: token = +otplib.totp.generate(secret)

  $: qrPackage = {
    timestamp: curMs,
    resourceId: data,
    otp: token,
    stringId: resourceId,
  }
  $: displayPackage = {
    timestamp: curMs,
    resourceId: data,
    otp: token,
  }
  $: {
    dispatch('scan', qrPackage)
  }

  updateQr()

  function intFromBytes(byteArr) {
    return byteArr.reduce((a, c, i) => a + c * 2 ** (56 - i * 8), 0)
  }

  async function updateQr() {
    if (live) {
      curMs = new Date().getTime() - delay
    }
    const segments = [
      { data: curMs, mode: 'numeric' },
      { data: data, mode: 'numeric' },
      { data: token, mode: 'numeric' },
    ]
    qrcode.toCan
    const qr = await qrcode.toCanvas(
      document.getElementById('canvas'),
      segments,
      {
        errorCorrectionLevel: 'M',
        version: 4,
      },
    )
    img = qr
    token = +otplib.totp.generate(secret)
  }

  setInterval(() => {
    updateQr()
  }, 100)
</script>

<style>
  :global(img) {
    image-rendering: crisp-edges;
  }
</style>

<div class="flex justify-around items-center">
  <canvas id="canvas" class="w-30 h-30 mr-6" />
  <pre>
    <code>{JSON.stringify(displayPackage, null, 2)}</code>
  </pre>
</div>
