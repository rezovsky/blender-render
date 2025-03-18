<template>
  <el-card style="max-width: 100%">
    <template #header>
      <el-row align="middle" justify="space-between">
        <el-col :span="2">
          <span>Текущая задача</span>
        </el-col>
        <el-col :span="22">
          <el-progress :text-inside="true" :stroke-width="26" :percentage="currentTask?.progress || 0" />
        </el-col>
      </el-row>
    </template>

    <!-- Вся информация в одну строку -->
    <el-row v-if="currentTask" justify="space-between" align="middle" class="task-row">
      <!-- Превью рендера -->
      <el-col :span="6" class="preview-container">
        <el-image v-if="currentTask.previewPath" :src="currentTask.previewPath" class="preview-image" fit="contain" />
      </el-col>

      <!-- Детали рендера -->
      <el-col :span="4" class="info-container">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Тип">{{ currentTask.renderType === "animation" ? "Анимация" : "Кадр" }}</el-descriptions-item>
          <el-descriptions-item label="Разрешение">{{ currentTask.resolutionX }} x {{ currentTask.resolutionY }}</el-descriptions-item>
          <el-descriptions-item label="Тайлы">{{ currentTask.tileSize }} px</el-descriptions-item>
          <el-descriptions-item label="Файл">{{ currentTask.filePath }}</el-descriptions-item>
        </el-descriptions>
      </el-col>

      <!-- Прогресс кадры -->
      <el-col :span="3" class="progress-container">
        <div class="progress-title">Кадры</div>
        <el-progress type="circle" :percentage="frameProgress" :width="100">
          <div class="progress-value">{{ currentTask.currentFrame }}/{{ currentTask.frameEnd }}</div>
        </el-progress>
      </el-col>
      
      <!-- Сетка рендера -->
      <el-col :span="5" class="progress-container">
        <div class="progress-title">Тайлы</div>
        <div>
        <RenderGrid 
          :key="renderKey"
          :imageWidth="currentTask.resolutionX" 
          :imageHeight="currentTask.resolutionY" 
          :tileSize="currentTask.tileSize" 
          :displayHeight="100"
          :filledTiles="currentTask.currentTile || 0"
        />
      </div>
      </el-col>

      <!-- Прогресс сэмплы -->
      <el-col :span="3" class="progress-container">
        <div class="progress-title">Сэмплы</div>
        <el-progress type="circle" :percentage="sampleProgress" :width="100">
          <div class="progress-value">{{ currentTask.currentSample }}/{{ currentTask.samples }}</div>
        </el-progress>
      </el-col>
    </el-row>
  </el-card>
</template>


<script setup>
import { computed, getCurrentInstance, watch, ref } from "vue";
import RenderGrid from "./RenderGrid.vue";
import { toCamelCase } from "@/utils"; // Функция конвертации

const { proxy } = getCurrentInstance();
const queueItems = ref([]); // Реактивное хранилище задач
const renderKey = ref(0); // Ключ для обновления RenderGrid

// Следим за изменением данных и конвертируем в camelCase
watch(
  () => proxy.$queueItems.value, 
  (newVal) => {
    console.log("📌 Обновление данных (до конвертации):", newVal);
    queueItems.value = newVal.map(toCamelCase);
    console.log("🚀 Преобразовано в camelCase:", queueItems.value);
    renderKey.value++; // Обновляем RenderGrid
  },
  { deep: true, immediate: true }
);

// Определяем текущую задачу
const currentTask = computed(() => 
  queueItems.value.find(task => task.status === "running") || null
);

// Прогресс рендера (кадры)
const frameProgress = computed(() => {
  if (!currentTask.value?.frameEnd || currentTask.value.frameEnd === 0) return 0;
  return Math.round(
    ((currentTask.value.currentFrame || 0) / currentTask.value.frameEnd) * 100
  );
});

// Прогресс рендера (сэмплы)
const sampleProgress = computed(() => {
  if (!currentTask.value?.samples || currentTask.value.samples === 0) return 0;
  return Math.round(
    ((currentTask.value.currentSample || 0) / currentTask.value.samples) * 100
  );
});

// Лог изменений текущей задачи
watch(currentTask, (newVal) => {
  console.log("🎯 Текущая задача:", JSON.stringify(newVal, null, 2));
}, { deep: true, immediate: true });
</script>

<style scoped>
.task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.grid-container {
  display: flex;
  justify-content: center;
  flex-grow: 1;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 200px;
}

.preview-image {
  width: 100%;
  max-height: 120px;
  border-radius: 8px;
  object-fit: contain;
  background-color: #222;
  padding: 5px;
}

.info-container {
  flex-grow: 1;
  display: flex;
  justify-content: center;
}

.progress-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-width: 120px;
  gap: 5px;
}

.progress-title {
  font-size: 14px;
  font-weight: bold;
  text-align: center;
}

.progress-label {
  font-size: 14px;
  font-weight: bold;
}

.progress-value {
  font-size: 12px;
}
</style>
