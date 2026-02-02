<template>
  <div class="app-container">
    <header class="header">
      <h1>NetNexus 🛡️ 智能网络运维平台</h1>
      <span class="status-dot"></span> 在线
    </header>

    <div class="chat-box" ref="chatBoxRef">
      <div v-if="messages.length === 0" class="empty-state">
        🤖 你好，我是运维助手。请下达指令，例如：“检查接口状态”
      </div>

      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message-row"
        :class="msg.role === 'user' ? 'user-row' : 'ai-row'"
      >
        <div class="avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        
        <div class="bubble">
          <div class="bubble-content" style="white-space: pre-wrap;">{{ msg.content }}</div>
        </div>
      </div>

      <div v-if="loading" class="message-row ai-row">
        <div class="avatar">🤖</div>
        <div class="bubble thinking">
          正在分析网络状态...
        </div>
      </div>
    </div>

    <div class="input-area">
      <input 
        v-model="inputQuery" 
        @keyup.enter="sendMessage"
        type="text" 
        placeholder="请输入运维指令..." 
        :disabled="loading"
      />
      <button @click="sendMessage" :disabled="loading || !inputQuery">
        {{ loading ? '执行中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import axios from 'axios';

// 数据状态
const messages = ref([]);
const inputQuery = ref('');
const loading = ref(false);
const chatBoxRef = ref(null);

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (chatBoxRef.value) {
    chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight;
  }
};

// 发送消息
const sendMessage = async () => {
  if (!inputQuery.value.trim()) return;

  const userText = inputQuery.value;
  
  // 1. 添加用户消息上屏
  messages.value.push({ role: 'user', content: userText });
  inputQuery.value = ''; // 清空输入框
  loading.value = true;
  scrollToBottom();

  try {
    // 2. 调用后端 API
    const res = await axios.post('http://127.0.0.1:8000/chat', {
      query: userText
    });

    // 3. 添加 AI 回复上屏
    messages.value.push({ role: 'ai', content: res.data.response });
  } catch (error) {
    messages.value.push({ role: 'ai', content: `❌ 系统错误: ${error.message}` });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};
</script>

<style scoped>
/* 简单的 CSS 样式，模拟控制台风格 */
.app-container {
  max-width: 800px;
  margin: 0 auto;
  height: 95vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  font-family: 'Segoe UI', sans-serif;
}

.header {
  background-color: #2c3e50;
  color: white;
  padding: 15px;
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.header h1 { margin: 0; font-size: 18px; }
.status-dot {
  width: 10px; height: 10px; background: #2ecc71; border-radius: 50%;
  box-shadow: 0 0 5px #2ecc71;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
}

.empty-state {
  text-align: center; color: #999; margin-top: 50px;
}

.message-row {
  display: flex; gap: 10px; margin-bottom: 20px;
}
.user-row { flex-direction: row-reverse; }

.avatar {
  width: 40px; height: 40px; background: #eee; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}

.bubble {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 10px;
  line-height: 1.5;
  font-size: 14px;
}
.user-row .bubble {
  background-color: #409eff; color: white;
  border-radius: 10px 0 10px 10px;
}
.ai-row .bubble {
  background-color: #f4f4f5; color: #333;
  border-radius: 0 10px 10px 10px;
  border: 1px solid #e9e9eb;
}

.thinking { color: #909399; font-style: italic; }

.input-area {
  padding: 15px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex; gap: 10px;
}
input {
  flex: 1; padding: 10px; border: 1px solid #dcdfe6; border-radius: 4px; outline: none;
}
input:focus { border-color: #409eff; }
button {
  padding: 0 20px; background: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer;
}
button:disabled { background: #a0cfff; cursor: not-allowed; }
</style>