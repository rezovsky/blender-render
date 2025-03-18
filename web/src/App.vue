<template>
  <el-container>
    <el-header>
      <HeaderComponent />
      <el-button @click="toggleDark()" style="margin-left: 20px;">
        Переключить тему
      </el-button>
    </el-header>
    <el-main>
      <el-row :gutter="20">
        <el-col :span="12">
          <Browser />
        </el-col>
        <el-col :span="12">
          <Queue :queueItems="queueItems" />
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="24">
          <TaskInfo />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { watchEffect } from "vue";
import { useDark, useToggle } from "@vueuse/core";
import HeaderComponent from './components/HeaderComponent.vue';
import Browser from './components/BrowserComponent.vue';
import Queue from './components/QueueComponent.vue';
import TaskInfo from './components/TaskInfoComponent.vue';

const queueItems = Array.from({ length: 14 }, (_, index) => index + 1);

// Автоопределение системной темы
const isDark = useDark();
const toggleDark = useToggle(isDark);

// Автоматическое применение темы
watchEffect(() => {
  if (isDark.value) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
});
</script>

<style scoped>
.el-card {
  margin-bottom: 20px;
}

.el-header {
  margin-bottom: 20px;
}

.dark {
  background: #121212;
  color: #fff;
}
</style>
