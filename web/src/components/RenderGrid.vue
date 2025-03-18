<template>
  <svg :width="svgWidth" :height="props.displayHeight" class="flipped-svg">
    <rect
      v-for="(tile, i) in tiles"
      :key="i"
      :x="tile.x"
      :y="tile.y"
      :width="tile.width"
      :height="tile.height"
      :fill="i < props.filledTiles ? '#20a0ff' : '#444'" 
      stroke="black"
      class="tile"
    />
  </svg>
</template>

<script setup>
import { ref, computed, watchEffect } from "vue";

const props = defineProps({
  imageWidth: { type: Number, default: 1920 },
  imageHeight: { type: Number, default: 1080 },
  tileSize: { type: Number, default: 512 },
  displayHeight: { type: Number, default: 300 },
  filledTiles: { type: Number, default: 0 } // 🔹 Реактивное обновление
});

// 🔹 Коэффициент масштабирования
const scale = computed(() => props.displayHeight / props.imageHeight);

// 🔹 Ширина `SVG`
const svgWidth = computed(() => props.imageWidth * scale.value);

// 🔹 Количество столбцов и строк
const cols = computed(() => Math.ceil(props.imageWidth / props.tileSize));
const rows = computed(() => Math.ceil(props.imageHeight / props.tileSize));

// 🔹 Размер плитки с учётом масштаба
const tileSizeScaled = computed(() => props.tileSize * scale.value);

// 🔹 Генерация сетки тайлов
const tiles = ref([]);

// 🔄 Следим за изменением количества заполненных тайлов
watchEffect(() => {
  console.log("🟢 Обновление сетки, заполненные тайлы:", props.filledTiles);
});

function generateTiles() {
  tiles.value = [];
  for (let row = 0; row < rows.value; row++) {
    for (let col = 0; col < cols.value; col++) {
      let fractionW = (col + 1) * props.tileSize > props.imageWidth ? (props.imageWidth % props.tileSize) / props.tileSize : 1;
      let fractionH = (row + 1) * props.tileSize > props.imageHeight ? (props.imageHeight % props.tileSize) / props.tileSize : 1;

      tiles.value.push({
        x: col * tileSizeScaled.value,
        y: row * tileSizeScaled.value,
        width: tileSizeScaled.value * fractionW,
        height: tileSizeScaled.value * fractionH,
      });
    }
  }
}

// 🔹 Генерация сетки при загрузке
generateTiles();
</script>

<style scoped>
.tile {
  transition: fill 0.3s ease-in-out;
}

.flipped-svg {
  transform: scaleY(-1);
}
</style>
