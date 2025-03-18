<template>
  <el-card
    class="task-card"
    @mouseenter="hover = true"
    @mouseleave="hover = false"
    :class="statusClass"
  >
    <template #header>
      <div class="card-header">
        <span class="status-icon">{{ statusIcon }}</span>
        <span class="task-number">№{{ localTask.id }}</span>
        <span class="task-path">{{ localTask.filePath }}</span>
        <div class="task-controls" v-show="hover">
          <el-button
            size="small"
            text
            :disabled="localTask.status === 'running'"
            @click="startTask"
          >
            ▶
          </el-button>
          <el-button
            size="small"
            text
            :disabled="localTask.status !== 'running'"
            @click="pauseTask"
          >
            ⏸
          </el-button>
          <el-button
            size="small"
            text
            :disabled="localTask.status !== 'running'"
            @click="stopTask"
          >
            ⏹
          </el-button>
          <el-button size="small" text type="danger" @click="deleteTask">
            ❌
          </el-button>
        </div>
      </div>
    </template>

    <div class="task-info">
      <span v-if="localTask.renderType === 'static'">Кадр ({{ localTask.frame }})</span>
      <span v-else>Анимация ({{ localTask.frameStart }} - {{ localTask.frameEnd }})</span>
    </div>

    <el-progress :text-inside="true" :stroke-width="15" :percentage="localTask.progress" />
  </el-card>
</template>

<script setup>
import { ref, reactive, watch, computed } from "vue";
import { apiRequest } from "@/api";

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(["updateTask", "deleteTask"]);

const hover = ref(false);
const localTask = reactive({ ...props.task });

watch(() => props.task, (newTask) => {
  Object.assign(localTask, newTask);
}, { deep: true });

const statusIcon = computed(() => {
  switch (localTask.status) {
    case "running":
      return "▶";     // Синий (визуально стрелка пуска)
    case "paused":
      return "⏸";     // Пауза
    case "completed":
      return "✅";     // Готово (галочка)
    case "stopped":
      return "⏹";     // Стоп
    default:
      return "⚫";     // Неизвестно
  }
});

const statusClass = computed(() => {
  return `status-${localTask.status}`;
});

const startTask = async () => {
  try {
    await apiRequest("POST", `/tasks/start/${localTask.id}`);
    localTask.status = "running";
    emit("updateTask", localTask);
  } catch (error) {
    console.error("Ошибка запуска задачи:", error);
  }
};

const pauseTask = async () => {
  try {
    await apiRequest("POST", `/tasks/pause/${localTask.id}`);
    localTask.status = "paused";
    emit("updateTask", localTask);
  } catch (error) {
    console.error("Ошибка приостановки задачи:", error);
  }
};

const stopTask = async () => {
  try {
    await apiRequest("POST", `/tasks/stop/${localTask.id}`);
    localTask.status = "stopped";
    localTask.progress = 0;
    emit("updateTask", localTask);
  } catch (error) {
    console.error("Ошибка остановки задачи:", error);
  }
};

const deleteTask = async () => {
  try {
    await apiRequest("DELETE", `/tasks/delete/${localTask.id}`);
    emit("deleteTask", localTask.id);
  } catch (error) {
    console.error("Ошибка удаления задачи:", error);
  }
};
</script>

<style scoped>
.task-card {
  position: relative;
  margin-bottom: 10px;
  transition: border 0.3s;
}

.status-running {
  border: 2px solid #3498db; /* Синий */
}

.status-paused {
  border: 2px solid #f1c40f; /* Жёлтый */
}

.status-completed {
  border: 2px solid #2ecc71; /* Зелёный */
}

.status-stopped {
  border: 2px solid #95a5a6; /* Серый */
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.status-icon {
  margin-right: 5px;
  font-size: 16px;
}

.task-number {
  font-weight: bold;
  margin-right: 10px;
}

.task-path {
  flex-grow: 1;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
  font-size: 14px;
  color: #bbb;
}

.task-controls {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.6);
  border-radius: 5px;
  padding: 2px 5px;
  display: flex;
  gap: 5px;
  align-items: center;
}

.task-controls .el-button {
  padding: 2px;
  min-width: 24px;
  height: 24px;
  font-size: 14px;
  color: white;
}

.task-info {
  margin-top: 5px;
  font-size: 14px;
  font-weight: bold;
  color: #ddd;
}
</style>
