import { createApp, ref } from "vue";
import App from "./App.vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "element-plus/theme-chalk/dark/css-vars.css";
import "./assets/style.css";

const app = createApp(App);

// 🔥 Глобальная переменная для очереди задач (теперь РЕАКТИВНАЯ)
app.config.globalProperties.$queueItems = ref([]);

// Отключение всех предупреждений
app.config.warnHandler = () => null;

app.use(ElementPlus);
app.mount("#app");
