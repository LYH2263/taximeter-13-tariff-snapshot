<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const current = ref(null)
const error = ref('')
const openId = ref('')

const loadList = async () => { items.value = (await getJSON('/api/history')).items }
const open = async (id) => {
  error.value = ''
  current.value = null
  try {
    current.value = await getJSON(`/api/history/${id}`)
  } catch (e) {
    error.value = e.message
  }
}
const openTyped = async () => {
  if (openId.value !== '' && Number.isFinite(Number(openId.value))) await open(Number(openId.value))
}
onMounted(loadList)
</script>
<template>
  <div class="page">
    <h1>记录</h1>
    <div class="panel">
      <label>按编号打开 <input type="number" v-model.number="openId" @keyup.enter="openTyped" /></label>
      <button style="margin-left:0.5rem" @click="openTyped">打开</button>
      <span v-if="error" style="color:#ff7b6b;margin-left:0.5rem">{{ error }}</span>
    </div>
    <table>
      <tr v-for="h in items" :key="h.id">
        <td><a href="#" @click.prevent="open(h.id)">#{{ h.id }}</a></td>
        <td>{{ h.kind }}</td>
        <td>{{ h.created_at }}</td>
      </tr>
    </table>

    <div v-if="current" class="panel" style="margin-top:1rem">
      <h3>记录 #{{ current.id }}（{{ current.kind }}）</h3>
      <p style="color:var(--muted)">{{ current.created_at }}</p>

      <template v-if="current.kind === 'fare'">
        <p class="hero-num">应付 ¥{{ current.result.total }}</p>
        <p>拆解：起步 {{ current.result.start }} · 里程 {{ current.result.mileage }} · 低速 {{ current.result.slow_fee }}</p>
        <p>里程 {{ current.result.distance_km }} 公里 · 低速 {{ current.result.slow_min }} 分钟 · {{ current.result.night ? '夜间' : '白天' }}</p>
      </template>
      <template v-else-if="current.kind === 'compare'">
        <p class="hero-num">白天 ¥{{ current.result.day_total }} · 夜间 ¥{{ current.result.night_total }} · 差 ¥{{ current.result.delta }}</p>
        <p>白天拆解：起步 {{ current.result.day.start }} · 里程 {{ current.result.day.mileage }} · 低速 {{ current.result.day.slow_fee }}</p>
        <p>夜间拆解：起步 {{ current.result.night.start }} · 里程 {{ current.result.night.mileage }} · 低速 {{ current.result.night.slow_fee }}</p>
      </template>

      <h4>写入时运价快照</h4>
      <template v-if="current.tariff_snapshot">
        <table>
          <tr><th>起步价</th><th>含公里</th><th>每公里</th><th>低速单价</th><th>夜间系数</th></tr>
          <tr>
            <td>{{ current.tariff_snapshot.start_price }}</td>
            <td>{{ current.tariff_snapshot.start_include_km }}</td>
            <td>{{ current.tariff_snapshot.per_km }}</td>
            <td>{{ current.tariff_snapshot.per_slow_min }}</td>
            <td>{{ current.tariff_snapshot.night_factor }}</td>
          </tr>
        </table>
      </template>
      <p v-else style="color:#ff7b6b">该记录写入时未留存运价快照。</p>
    </div>
  </div>
</template>
