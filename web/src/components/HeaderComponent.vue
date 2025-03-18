<template>
  <el-card>
    <el-row>
      <el-col :span="10">
        <el-space>
          <el-text class="mx-1" size="large">Статус:</el-text>
          <el-text class="mx-1" type="success" size="large">Запущено</el-text>
        </el-space>
      </el-col>
      <el-col :span="13"></el-col>
      <el-col :span="1">
        <el-button plain @click="openSettings">⚙️</el-button>
        <el-dialog v-model="settingsVisible" title="Настройки" width="900px">
          <el-form label-width="auto">
            <el-form-item label="Запуск Blender">
              <el-radio-group v-model="settings.blenderMode">
                <el-radio label="path">В переменной PATH</el-radio>
                <el-radio label="manual">Указать путь вручную</el-radio>
              </el-radio-group>
              <el-text type="info" size="small">
                Если Blender установлен в PATH, путь указывать не нужно.
              </el-text>
            </el-form-item>
            <el-form-item v-if="settings.blenderMode === 'manual'" label="Путь к Blender">
              <el-input v-model="settings.blenderPath" placeholder="Введите путь до blender.exe" />
              <el-text type="info" size="small">
                Например: <code>C:\Program Files\Blender Foundation\Blender 4.3\blender.exe</code>
              </el-text>
            </el-form-item>
            <el-form-item label="Папка с проектами">
              <el-input v-model="settings.projectsPath" placeholder="Введите путь к проектам" />
              <el-text type="info" size="small">
                Например: <code>/mnt/projects</code> или <code>C:\Users\User\Projects</code>
              </el-text>
            </el-form-item>
            <el-form-item label="Использовать отдельную папку рендера">
              <el-switch v-model="settings.useRenderFolder" />
            </el-form-item>
            <el-form-item v-if="settings.useRenderFolder" label="Папка для рендера">
              <el-input v-model="settings.renderFolderPath" placeholder="Введите путь к рендеру" />
              <el-text type="info" size="small">
                Если включено, файлы рендера сохраняются в указанную папку.
              </el-text>
            </el-form-item>
            <el-form-item label="Автозапуск очереди при старте">
              <el-switch v-model="settings.autoStartQueue" />
              <el-text type="info" size="small">
                При запуске сервера сразу начать выполнение очереди рендеринга.
              </el-text>
            </el-form-item>
            <el-form-item label="Автозапуск задач">
              <el-switch v-model="settings.autoStartTasks" />
              <el-text type="info" size="small">
                При добавлении новой задачи в очередь она сразу запускается.
              </el-text>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button type="primary" @click="updateSettings">Сохранить</el-button>
            <el-button @click="settingsVisible = false">Закрыть</el-button>
          </template>
        </el-dialog>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { apiRequest } from "@/api";

const settingsVisible = ref(false);
const settings = ref({
  blenderMode: "path",
  blenderPath: "",
  projectsPath: "",
  useRenderFolder: false,
  renderFolderPath: "",
  autoStartQueue: false,
  autoStartTasks: false,
});

const loadSettings = async () => {
  try {
    settings.value = await apiRequest("GET", "/settings/");
    if (!settings.value.projectsPath) {
      settingsVisible.value = true;
    }
  } catch (error) {
    console.error("Не удалось загрузить настройки");
  }
};

const openSettings = async () => {
  await loadSettings();
  settingsVisible.value = true;
};



const updateSettings = async () => {
  try {
    await apiRequest("PUT", "/settings/", settings.value);
    settingsVisible.value = false;
  } catch (error) {
    console.error("Ошибка при сохранении настроек");
  }
};


watch(settings, (newSettings) => {
  if (newSettings.blenderMode === "manual" && !newSettings.blenderPath) {
    settings.value.blenderPath = "";
  }
});

onMounted(loadSettings);
</script>

<style scoped>
.el-card {
  margin-bottom: 20px;
}
.el-header {
  margin-bottom: 20px;
}
.el-text {
  display: block;
  margin-top: 5px;
}
</style>
