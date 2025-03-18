<template>
  <el-card style="max-width: 100%">
    <template #header>
      <div class="card-header">
        <span>Браузер</span>
      </div>
    </template>
    <el-scrollbar height="300px">
      <el-tree-v2
        v-loading="loading"
        :data="data"
        :props="props"
        :height="300"
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <el-icon v-if="data.children" class="folder-icon">
              <Folder />
            </el-icon>
            <el-icon v-else class="file-icon">
              <Document />
            </el-icon>
            <span :class="{ 'folder-label': data.children, 'file-label': !data.children }">{{ node.label }}</span>
            <span 
              v-if="!data.children && data.label.endsWith('.blend')" 
              class="add-task-icon" 
              @click.stop="openAddTaskDialog(data.value)"
            >➜</span>
          </div>
        </template>
      </el-tree-v2>
    </el-scrollbar>

    <!-- Подключаем диалог добавления задачи -->
    <AddTaskDialog v-model="taskDialogVisible" :file-path="selectedFilePath" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { apiRequest } from "@/api";
import { Folder, Document } from "@element-plus/icons-vue";
import AddTaskDialog from "@/components/AddTaskDialog.vue"; // Подключаем компонент

const data = ref([]);
const loading = ref(true);
const taskDialogVisible = ref(false);
const selectedFilePath = ref("");

const props = {
  value: "id",
  label: "label",
  children: "children",
};


const loadProjectTree = async () => {
  try {
    const settingsResponse = await apiRequest(
            "GET",
            '/settings/',
          );
    const response = await apiRequest(
        "GET",
        `/browser_tree`,
        { path: settingsResponse.projectsPath,
          mask: 'blend'
         }
      );
    data.value = response;
  } catch (error) {
    console.error("Ошибка при загрузке дерева проектов:", error);
  } finally {
    loading.value = false;
  }
};

const startCyclicalScan = async () => {
  try {
    const response = await apiRequest("POST", "/start_cyclical_scan");
    console.log(response);

  } catch (error) {
    console.error("Ошибка при запуске циклического сканирования:", error);
  }
};

const treeReload = () => {
  setInterval(() => {
    loadProjectTree();
  }, 30000);
};

const openAddTaskDialog = (value) => {
  selectedFilePath.value = value;
  taskDialogVisible.value = true;
};

onMounted(loadProjectTree);
onMounted(treeReload);
onMounted(startCyclicalScan);
</script>


<style scoped>
.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Цвета для иконок и текстов в зависимости от темы */
.folder-icon {
  color: var(--el-color-primary); /* Автоматически адаптируется */
}
.file-icon {
  color: var(--el-color-success); /* Автоматически адаптируется */
}

/* Светлая тема */
.folder-label,
.file-label {
  font-weight: bold;
  color: #303133;
}

.file-label {
  color: #606266;
}

.add-task-icon {
  cursor: pointer;
  margin-left: auto;
  color: var(--el-color-primary);
  font-size: 16px;
  font-weight: bold;
}

.add-task-icon:hover {
  color: var(--el-color-primary-light-3);
}

/* Стили для превью */
.preview-container {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--el-border-color);
  border-radius: 4px;
  background-color: var(--el-fill-color-light);
  margin-bottom: 10px;
}

.preview-placeholder {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

/* Темная тема */
.dark .folder-label,
.dark .file-label {
  color: #e0e0e0; /* Светлый текст в тёмной теме */
}

.dark .preview-container {
  background-color: #2c2c2c;
  border-color: #555;
}

.dark .preview-placeholder {
  color: #bbb;
}
</style>

