<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const distance_km = ref(8)
const slow_min = ref(3)
const night = ref(false)
const out = ref(null)
const run = async () => { out.value = await postJSON('/api/fare', { distance_km: distance_km.value, slow_min: slow_min.value, night: night.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>打表试算</h1>
    <div class="panel">
      <label>公里 <input type="number" v-model.number="distance_km" /></label>
      <label>低速分钟 <input type="number" v-model.number="slow_min" /></label>
      <label><input type="checkbox" v-model="night" /> 夜间</label>
      <button @click="run">计算</button>
    </div>
    <div v-if="out" class="panel">
      <p class="hero-num">¥{{ out.total }}</p>
      <p>起步 {{ out.start }} · 里程 {{ out.mileage }} · 低速 {{ out.slow_fee }}<template v-if="out.night"> · 夜间系数 ×{{ out.night_factor }}</template></p>
      <p class="muted">本次使用运价:起步价 ¥{{ out.tariff.start_price }} · 含 {{ out.tariff.start_include_km }} 公里 · 每公里 ¥{{ out.tariff.per_km }} · 低速每分钟 ¥{{ out.tariff.per_slow_min }} · 夜间系数 ×{{ out.tariff.night_factor }}</p>
      <p v-if="out.run_id" class="muted">已写入记录 #{{ out.run_id }}</p>
    </div>
  </div>
</template>
