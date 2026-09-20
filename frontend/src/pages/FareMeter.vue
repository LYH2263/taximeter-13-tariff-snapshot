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
      <label style="margin-left:0.5rem">低速分钟 <input type="number" v-model.number="slow_min" /></label>
      <label style="margin-left:0.5rem"><input type="checkbox" v-model="night" /> 夜间</label>
      <button style="margin-left:0.5rem" @click="run">计算</button>
    </div>
    <template v-if="out">
      <p class="hero-num">¥{{ out.total }}</p>
      <div class="panel">
        <p>起步 {{ out.start }} · 里程 {{ out.mileage }} · 低速 {{ out.slow_fee }}</p>
        <p style="color:var(--muted)">本次运价：起步价 {{ out.start_price }} · 含公里 {{ out.start_include_km }} · 每公里 {{ out.per_km }} · 低速单价 {{ out.per_slow_min }} · 夜间系数 {{ out.night_factor }}</p>
      </div>
    </template>
  </div>
</template>
