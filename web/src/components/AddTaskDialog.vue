<template>
  <el-dialog v-model="dialogVisible" title="Добавить задачу" width="1000px">
    <el-form label-width="150px">
      <!-- Основное содержимое формы -->
      <el-divider content-position="left">Параметры рендера</el-divider>

      <el-skeleton v-if="loading" animated />
      <el-form-item v-if="!loading" label="Тип рендера">
        <el-radio-group v-model="renderType">
          <el-radio value="static">Статический кадр</el-radio>
          <el-radio value="animation">Анимация</el-radio>
        </el-radio-group>
      </el-form-item>

      <div v-if="!loading">
        <el-form-item v-if="renderType === 'static'" label="Кадр">
          <el-input-number v-model="frameCurrent" :min="1" />
        </el-form-item>

        <el-form-item v-if="renderType === 'animation'" label="Диапазон кадров">
          <div style="display: flex; gap: 10px">
            <el-input-number v-model="frameStart" :min="1" label="Начало" />
            <el-input-number v-model="frameEnd" :min="frameStart" label="Конец" />
          </div>
        </el-form-item>
      </div>

      <el-divider content-position="left">Сохранение результатов рендера</el-divider>
      <el-skeleton v-if="loading" animated />
      <el-form-item v-else-if="foldersPaths" label="Путь сохранения">
        <div class="folder-selection">
          <el-tree-select v-model="selectedFolder" :data="foldersPaths" :render-after-expand="false" show-checkbox
            check-on-click-node check-strictly placeholder="Выберите папку" style="width: 300px"
            @change="handleSelectionChange" />
          <div class="new-folder">
            <el-input v-model="newFolderName" placeholder="Новая папка" style="width: 200px" />
            <el-button v-if="newFolderName" type="primary" plain @click="createNewFolder">Создать</el-button>
          </div>
        </div>
      </el-form-item>

      <el-divider content-position="left">Информация о файле</el-divider>
      <el-skeleton v-if="loading" animated />
      <el-descriptions v-else-if="fileInfo" border>
        <el-descriptions-item label="Путь к файлу">
          {{ filePath }}
        </el-descriptions-item>
        <el-descriptions-item label="Разрешение">
          {{ fileInfo?.resolutionX }} x {{ fileInfo?.resolutionY }}
        </el-descriptions-item>
        <el-descriptions-item label="Семплы">
          {{ fileInfo?.samples }}
        </el-descriptions-item>
        <el-descriptions-item label="Размер тайлов">
          {{ fileInfo?.tileSize }}
        </el-descriptions-item>
        <el-descriptions-item label="Движок">
          {{ fileInfo?.engine }}
        </el-descriptions-item>
        <el-descriptions-item label="Предпросмотр" v-if="fileInfo?.previewPath">
          <img :src="fileInfo.previewPath" alt="Предпросмотр" style="height: 200px; max-width: 100%;" />
        </el-descriptions-item>
      </el-descriptions>
      <el-empty v-else description="Нет данных о файле" />
    </el-form>

    <!-- Добавленный слот footer с кнопками -->
    <template v-slot:footer>
      <div class="dialog-footer">
        <el-button @click="closeDialog">Отмена</el-button>
        <el-button type="primary" @click="addTask">Добавить</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watchEffect, watch, nextTick, defineModel, defineProps } from "vue";
import { apiRequest } from "@/api";

async function updateTreeData(response) {
  foldersPaths.value = response || [];
  await nextTick();
  console.log("Обновлённые данные:", foldersPaths.value);
}

const props = defineProps({
  filePath: String,
});

// Управляемые состояния
const dialogVisible = defineModel();
const renderType = ref("static");
const fileInfo = ref(null);
const selectedFolder = ref("");
const loading = ref(false);
const loading_tree = ref(true);
const curentFilePath = ref("");
const foldersPaths = ref([]);
const newFolderName = ref("");

// Управляемые состояния для кадров рендера
const frameCurrent = ref(0);
const frameStart = ref(1);
const frameEnd = ref(250);


function closeDialog() {
  dialogVisible.value = false;
}

async function addTask() {
  // ✅ Исправляем пути
  const normalizedFilePath = props.filePath.replace(/\\/g, "/");

  // ✅ Если папка не выбрана, создаём её автоматически
  let selectedFolderPath = selectedFolder.value ? selectedFolder.value.replace(/\\/g, "/") : null;

  if (!selectedFolderPath) {
    const basePath = normalizedFilePath.split("/").slice(0, -1).join("/"); // Корневая папка с .blend
    const taskNumber = Date.now(); // 🔥 Генерируем уникальный ID (можно заменить на API-номер задачи)
    selectedFolderPath = `${basePath}/render/${taskNumber}`;
  }

  const task = {
    filePath: normalizedFilePath,
    renderType: renderType.value,
    frame: renderType.value === "static" ? frameCurrent.value : null,
    frameStart: renderType.value === "animation" ? frameStart.value : null,
    frameEnd: renderType.value === "animation" ? frameEnd.value : null,
    selectedFolder: selectedFolderPath, // 🔥 Теперь это правильный путь
    resolutionX: fileInfo.value?.resolutionX || 0,
    resolutionY: fileInfo.value?.resolutionY || 0,
    samples: fileInfo.value?.samples || 1,
    tileSize: fileInfo.value?.tileSize || 16,
    engine: fileInfo.value?.engine || "CYCLES",
    previewPath: fileInfo.value?.previewPath || null,
  };

  console.log("🚀 Отправка задачи:", task);

  try {
    const response = await apiRequest("POST", "/tasks/add", task);
    console.log("✅ Задача успешно добавлена:", response);
    closeDialog();
  } catch (error) {
    console.error("❌ Ошибка при добавлении задачи:", error.response?.data || error.message);
  }
}



// Следим за изменением filePath
watchEffect(async () => {
  if (!props.filePath) return;

  loading.value = true;
  try {
    fileInfo.value = await apiRequest("GET", "/file_info", { filePath: props.filePath });
    curentFilePath.value = fileInfo.value?.filePath || "";

    frameCurrent.value = fileInfo.value?.frameCurrent || 1;
    frameStart.value = fileInfo.value?.frameStart || 1;
    frameEnd.value = fileInfo.value?.frameEnd || 250;
  } catch (error) {
    console.error("Ошибка при получении информации о файле:", error);
    fileInfo.value = null;
    curentFilePath.value = ""; // Очищаем путь при ошибке
  } finally {
    loading.value = false;
  }
});

async function refreshTree(newPath = curentFilePath.value) {
  if (!newPath) return;

  selectedFolder.value = "";
  loading_tree.value = true;

  console.log("newPath", newPath);

  const pathArray = newPath.split(/[\\/]/);
  const folderPath = pathArray.slice(0, -1).join("/");

  console.log("folderPath", folderPath);

  try {
    const response = await apiRequest("GET", "/folder_tree", { path: folderPath });
    updateTreeData(response);
  } catch (error) {
    console.error("Ошибка при загрузке дерева папок:", error);
    foldersPaths.value = [];
  } finally {
    loading_tree.value = false;
  }
}

watch(
  () => curentFilePath.value,
  (newPath) => refreshTree(newPath),
  { immediate: true }
);

// Функция поиска `value` в дереве
function findNodeByFullPath(nodes, fullPath) {
  const normalizedPath = fullPath.replace(/\\/g, "/");

  for (const node of nodes) {
    const nodePath = node.value.replace(/\\/g, "/");

    if (nodePath === normalizedPath) return node.value;

    if (node.children) {
      const found = findNodeByFullPath(node.children, fullPath);
      if (found) return found;
    }
  }
  return null;
}

function getDirectoryPath(fullPath) {
  return fullPath.replace(/\\/g, "/").split("/").slice(0, -1).join("/");
}

async function createNewFolder() {
  if (!props.filePath) {
    console.warn("Ошибка: `filePath` не указан!");
    return;
  }

  let mainPath = getDirectoryPath(props.filePath);

  let newFolderPath = selectedFolder.value
    ? selectedFolder.value + "/" + newFolderName.value
    : mainPath + "/" + newFolderName.value;

  newFolderPath = newFolderPath.replace(/\\/g, "/");

  console.log("Создаем новую папку:", newFolderPath);

  if (!newFolderName.value.trim()) {
    console.warn("Ошибка: имя папки пустое!");
    return;
  }

  try {
    newFolderName.value = "";
    await apiRequest("POST", "/create_folder", { path: newFolderPath });

    console.log("Папка успешно создана, обновляем дерево...");

    await refreshTree();
    await nextTick();

    const foundValue = findNodeByFullPath(foldersPaths.value, newFolderPath);
    if (foundValue) {
      selectedFolder.value = foundValue;
      console.log("Выбрана папка:", selectedFolder.value);
    } else {
      console.warn("Созданная папка не найдена в дереве!");
    }
  } catch (error) {
    console.error("Ошибка при создании папки:", error);
  }
}
</script>


<style scoped>
.el-text {
  display: block;
  margin-bottom: 5px;
}

.folder-selection {
  display: flex;
  align-items: center;
  gap: 10px;
  /* Отступы между элементами */
}

.new-folder {
  display: flex;
  align-items: center;
  gap: 10px;
  /* Отступ между input и кнопкой */
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
}
</style>
