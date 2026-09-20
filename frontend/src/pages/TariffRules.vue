<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'

const blank = { start_price: 0, start_include_km: 0, per_km: 0, per_slow_min: 0, night_factor: 1 }
const form = ref({ ...blank })
const current = ref(null)   // 库中现行运价
const err = ref('')
const savedTip = ref(false)
const preview = ref(null)   // 只读试算结果(不写记录)
const pDist = ref(5)
const pSlow = ref(2)
const pNight = ref(false)

const fill = (t) => {
  form.value = {
    start_price: t.start_price, start_include_km: t.start_include_km,
    per_km: t.per_km, per_slow_min: t.per_slow_min, night_factor: t.night_factor,
  }
}
const load = async () => { current.value = await getJSON('/api/tariff'); fill(current.value) }

const runPreview = async () => {
  preview.value = await postJSON('/api/fare', {
    distance_km: pDist.value, slow_min: pSlow.value, night: pNight.value, persist: false,
  })
}

const save = async () => {
  err.value = ''; savedTip.value = false
  try {
    current.value = await putJSON('/api/tariff', form.value)
  } catch (e) {
    err.value = '校验失败:起步价/每公里/低速单价须为正,含公里不得为负,夜间系数须大于零。库中运价未改动。'
    fill(current.value)
    return
  }
  fill(current.value)
  savedTip.value = true
  await runPreview()  // 保存后当场只读打表,跟随新运价,不写记录
}

onMounted(load)
</script>
<template>
  <div class="page"><h1>运价表</h1>
    <div class="panel" v-if="current">
      <h3>现行运价(库中)</h3>
      <p>起步价 ¥{{ current.start_price }} · 含 {{ current.start_include_km }} 公里 · 每公里 ¥{{ current.per_km }} · 低速每分钟 ¥{{ current.per_slow_min }} · 夜间系数 ×{{ current.night_factor }}</p>
    </div>
    <div class="panel">
      <h3>修改运价</h3>
      <label>起步价 <input type="number" step="0.1" v-model.number="form.start_price" /></label>
      <label>含公里 <input type="number" step="0.1" v-model.number="form.start_include_km" /></label>
      <label>每公里 <input type="number" step="0.1" v-model.number="form.per_km" /></label>
      <label>低速每分钟 <input type="number" step="0.1" v-model.number="form.per_slow_min" /></label>
      <label>夜间系数 <input type="number" step="0.01" v-model.number="form.night_factor" /></label>
      <button @click="save">保存</button>
      <p v-if="err" class="err">{{ err }}</p>
      <p v-if="savedTip" class="ok">已保存,以下为按新运价的只读试算(未写记录)。</p>
    </div>
    <div class="panel" v-if="preview">
      <h3>只读试算(不写记录)</h3>
      <label>公里 <input type="number" step="0.1" v-model.number="pDist" /></label>
      <label>低速分钟 <input type="number" step="0.1" v-model.number="pSlow" /></label>
      <label><input type="checkbox" v-model="pNight" /> 夜间</label>
      <button @click="runPreview">试算</button>
      <p class="hero-num">¥{{ preview.total }}</p>
      <p>起步 {{ preview.start }} · 里程 {{ preview.mileage }} · 低速 {{ preview.slow_fee }}</p>
      <p class="muted">本次使用运价:起步价 ¥{{ preview.tariff.start_price }} · 含 {{ preview.tariff.start_include_km }} 公里 · 每公里 ¥{{ preview.tariff.per_km }} · 低速每分钟 ¥{{ preview.tariff.per_slow_min }} · 夜间系数 ×{{ preview.tariff.night_factor }}</p>
    </div>
  </div>
</template>
