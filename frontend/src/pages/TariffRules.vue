<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const fields = [
  { key: 'start_price', label: '起步价', step: 0.1 },
  { key: 'start_include_km', label: '含公里', step: 0.1 },
  { key: 'per_km', label: '每公里', step: 0.1 },
  { key: 'per_slow_min', label: '低速单价', step: 0.1 },
  { key: 'night_factor', label: '夜间系数', step: 0.05 },
]
const form = ref({})
const error = ref('')
const saved = ref(null)
const preview = ref(null)
const previewInput = ref({ distance_km: 5, slow_min: 2, night: false })
const saving = ref(false)

const load = async () => {
  saved.value = await getJSON('/api/tariff')
  form.value = { ...saved.value }
  error.value = ''
}

const runPreview = async () => {
  preview.value = await postJSON('/api/fare', { ...previewInput.value, persist: false })
}

const save = async () => {
  error.value = ''
  saving.value = true
  try {
    saved.value = await postJSON('/api/tariff', { ...form.value })
    form.value = { ...saved.value }
    await runPreview()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

onMounted(async () => { await load(); await runPreview() })
</script>
<template>
  <div class="page">
    <h1>运价表</h1>
    <div v-if="saved" class="panel">
      <h3>现行运价</h3>
      <p>起步价 {{ saved.start_price }} · 含公里 {{ saved.start_include_km }} · 每公里 {{ saved.per_km }} · 低速单价 {{ saved.per_slow_min }} · 夜间系数 {{ saved.night_factor }}</p>
    </div>
    <div class="panel">
      <h3>修改运价</h3>
      <div v-for="f in fields" :key="f.key" style="margin:0.4rem 0">
        <label style="display:inline-block;width:90px">{{ f.label }}</label>
        <input type="number" :step="f.step" v-model.number="form[f.key]" />
      </div>
      <p v-if="error" style="color:#ff7b6b">{{ error }}</p>
      <button :disabled="saving" @click="save">保存</button>
    </div>
    <div v-if="preview" class="panel">
      <h3>按新运价只读打表（不写记录）</h3>
      <label>公里 <input type="number" v-model.number="previewInput.distance_km" /></label>
      <label style="margin-left:0.5rem">低速分钟 <input type="number" v-model.number="previewInput.slow_min" /></label>
      <label style="margin-left:0.5rem"><input type="checkbox" v-model="previewInput.night" /> 夜间</label>
      <button style="margin-left:0.5rem" @click="runPreview">试算</button>
      <p class="hero-num">¥{{ preview.total }}</p>
      <p>起步 {{ preview.start }} · 里程 {{ preview.mileage }} · 低速 {{ preview.slow_fee }}</p>
      <p style="color:var(--muted)">本次运价：起步价 {{ preview.start_price }} · 含公里 {{ preview.start_include_km }} · 每公里 {{ preview.per_km }} · 低速单价 {{ preview.per_slow_min }} · 夜间系数 {{ preview.night_factor }}</p>
    </div>
  </div>
</template>
