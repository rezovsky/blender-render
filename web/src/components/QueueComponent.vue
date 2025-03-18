<template>
  <el-card style="max-width: 100%">
    <template #header>
      <el-row align="middle" justify="space-between">
        <el-col :span="12">
          <span>Очередь ({{ queueItems.length }})</span>
        </el-col>

        <el-col :span="12" class="text-right">
          <el-button type="primary" @click="fetchQueue">🔄 Обновить</el-button>
          <el-button @click="clearQueue">🗑 Очистить</el-button>
        </el-col>
      </el-row>
    </template>

    <el-scrollbar height="300px">
      <draggable
        v-model="queueItems"
        item-key="id"
        animation="200"
        ghost-class="ghost"
        drag-class="dragging"
        @end="onDragEnd"
      >
        <template #item="{ element }">
          <QueueItem 
            :task="element"
            @updateTask="updateTask"
            @deleteTask="removeTask"
          />
        </template>
      </draggable>
    </el-scrollbar>
  </el-card>
</template>

<script setup>
import { getCurrentInstance, onMounted, onUnmounted } from "vue";
import draggable from "vuedraggable";
import QueueItem from "./QueueItem.vue";
import { apiRequest } from "@/api";

const { proxy } = getCurrentInstance(); // Получаем доступ к глобальным переменным
const queueItems = proxy.$queueItems; // ✅ Используем глобальную переменную

let intervalId = null;

const fetchQueue = async () => {
  try {
    const response = await apiRequest("GET", "/tasks/queue");
    queueItems.value = response;
    console.log("✅ Очередь загружена:", queueItems.value);
  } catch (error) {
    console.error("❌ Ошибка загрузки очереди:", error.response?.data || error.message);
  }
};

const clearQueue = async () => {
  try {
    await apiRequest("DELETE", "/tasks/clear");
    queueItems.value = [];
  } catch (error) {
    console.error("Ошибка очистки очереди:", error);
  }
};

const onDragEnd = async () => {
  const reorderedTasks = queueItems.value.map((task, index) => ({
    id: task.id,
    position: index,
  }));

  try {
    await apiRequest("PUT", "/tasks/reorder", reorderedTasks);
    console.log("✅ Порядок очереди сохранён");
  } catch (error) {
    console.error("❌ Ошибка сохранения порядка очереди:", error.response?.data || error.message);
  }
};

// 🔥 Обновление задачи в списке
const updateTask = (updatedTask) => {
  const index = queueItems.value.findIndex((task) => task.id === updatedTask.id);
  if (index !== -1) {
    queueItems.value[index] = updatedTask;
  }
};

// 🔥 Удаление задачи из списка
const removeTask = (taskId) => {
  queueItems.value = queueItems.value.filter((task) => task.id !== taskId);
};

// 🔄 Запуск автообновления списка задач
onMounted(() => {
  fetchQueue(); // Первый запрос при загрузке компонента
  intervalId = setInterval(fetchQueue, 1000); // Автообновление каждые 10 секунд
});

// 🛑 Очистка интервала при уничтожении компонента
onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>


<style>
.ghost {
  opacity: 0.5;
  background: #ddd;
}

.dragging {
  background: #f0f0f0;
}
</style>
