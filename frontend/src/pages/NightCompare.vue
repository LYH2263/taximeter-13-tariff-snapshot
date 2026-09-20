<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const distance_km = ref(18)
const slow_min = ref(12)
const c = ref(null)
const run = async () => { c.value = await postJSON('/api/compare', { distance_km: distance_km.value, slow_min: slow_min.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>昼夜对比</h1>
    <div class="panel">
      <label>公里 <input type="number" v-model.number="distance_km" /></label>
      <label style="margin-left:0.5rem">低速分钟 <input type="number" v-model.number="slow_min" /></label>
      <button style="margin-left:0.5rem" @click="run">对比</button>
    </div>
    <div v-if="c" class="panel">
      <p class="hero-num">白天 ¥{{ c.day_total }} · 夜间 ¥{{ c.night_total }} · 差 ¥{{ c.delta }}</p>
      <p style="color:var(--muted)">本次运价：起步价 {{ c.start_price }} · 含公里 {{ c.start_include_km }} · 每公里 {{ c.per_km }} · 低速单价 {{ c.per_slow_min }} · 夜间系数 {{ c.night_factor }}</p>
    </div>
  </div>
</template>
