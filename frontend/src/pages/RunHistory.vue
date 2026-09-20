<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const detail = ref(null)
const lookupId = ref('')
const err = ref('')
const due = (r) => r.kind === 'compare' ? `白天 ¥${r.result.day_total} / 夜间 ¥${r.result.night_total}` : `¥${r.result.total}`
const open = async (id) => {
  err.value = ''; detail.value = null
  try { detail.value = await getJSON(`/api/history/${id}`) }
  catch (e) { err.value = `记录 #${id} 不存在` }
}
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template>
  <div class="page"><h1>记录</h1>
    <div class="panel">
      <label>按编号打开 <input type="number" v-model="lookupId" /></label>
      <button @click="open(lookupId)">打开</button>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
    <table>
      <tr><th>编号</th><th>类型</th><th>时间</th><th>应付</th><th></th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ h.created_at }}</td><td>{{ due(h) }}</td>
        <td><a href="javascript:;" @click="open(h.id)">查看</a></td>
      </tr>
    </table>
    <div v-if="detail" class="panel">
      <h3>记录 #{{ detail.id }}({{ detail.kind }})</h3>
      <p v-if="detail.kind === 'compare'">
        应付:白天 ¥{{ detail.result.day_total }} · 夜间 ¥{{ detail.result.night_total }} · 差 ¥{{ detail.result.delta }}
      </p>
      <p v-else>
        <span class="hero-num">应付 ¥{{ detail.result.total }}</span><br />
        起步 {{ detail.result.start }} · 里程 {{ detail.result.mileage }} · 低速 {{ detail.result.slow_fee }}
      </p>
      <template v-if="detail.result.tariff">
        <h4>写入时运价快照</h4>
        <p>起步价 ¥{{ detail.result.tariff.start_price }} · 含 {{ detail.result.tariff.start_include_km }} 公里 · 每公里 ¥{{ detail.result.tariff.per_km }} · 低速每分钟 ¥{{ detail.result.tariff.per_slow_min }} · 夜间系数 ×{{ detail.result.tariff.night_factor }}</p>
      </template>
    </div>
  </div>
</template>
