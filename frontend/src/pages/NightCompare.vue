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
    <button @click="run">对比</button>
    <div v-if="c" class="panel">
      <p>白天 ¥{{ c.day_total }} · 夜间 ¥{{ c.night_total }} · 差 ¥{{ c.delta }}</p>
      <p class="muted">本次使用运价:起步价 ¥{{ c.tariff.start_price }} · 含 {{ c.tariff.start_include_km }} 公里 · 每公里 ¥{{ c.tariff.per_km }} · 低速每分钟 ¥{{ c.tariff.per_slow_min }} · 夜间系数 ×{{ c.tariff.night_factor }}</p>
      <p v-if="c.run_id" class="muted">已写入记录 #{{ c.run_id }}</p>
    </div>
  </div>
</template>
