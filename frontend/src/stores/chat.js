import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/axios.js'
import { useAuthStore } from './auth.js'

export const useChatStore = defineStore('chat', () => {
  const rooms = ref([])
  const activeRoom = ref(null)
  const messages = ref([])
  const onlineUsers = ref(new Set())
  const typingUsers = ref(new Map())
  let socket = null
  let typingTimeout = null

  const typingText = computed(() => {
    const users = [...typingUsers.value.values()]
    if (!users.length) return ''
    if (users.length === 1) return `${users[0]} is typing...`
    return `${users.slice(0, -1).join(', ')} and ${users.at(-1)} are typing...`
  })

async function fetchRooms() {
  const { data } = await api.get('/chat/rooms/')
  rooms.value = data.results ?? data
}

  async function joinRoom(room) {
    if (socket) {
      socket.close()
      socket = null
    }
    activeRoom.value = room
    onlineUsers.value = new Set()
    typingUsers.value = new Map()

    const { data } = await api.get(`/chat/rooms/${room.name}/messages/`)
    messages.value = data

    const auth = useAuthStore()
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${location.host}/ws/chat/${room.name}/?token=${auth.access}`
    socket = new WebSocket(url)

    socket.onmessage = ({ data }) => {
      handleEvent(JSON.parse(data))
    }
    socket.onerror = err => console.error('WebSocket error:', err)
    socket.onclose = () => console.log('WebSocket closed')
  }

  function handleEvent(event) {
    switch (event.type) {
      case 'message':
        messages.value.push(event)
        break
      case 'user_join':
        onlineUsers.value = new Set([...onlineUsers.value, event.user_id])
        break
      case 'user_leave':
        onlineUsers.value.delete(event.user_id)
        typingUsers.value.delete(event.user_id)
        break
      case 'typing':
        if (event.is_typing) {
          typingUsers.value.set(event.user_id, event.name)
        } else {
          typingUsers.value.delete(event.user_id)
        }
        break
    }
  }

  function sendMessage(content) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return
    socket.send(JSON.stringify({ type: 'message', content }))
  }

  function sendTyping(isTyping) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return
    socket.send(JSON.stringify({ type: 'typing', is_typing: isTyping }))
    if (isTyping) {
      clearTimeout(typingTimeout)
      typingTimeout = setTimeout(() => sendTyping(false), 2500)
    }
  }

  function leaveRoom() {
    if (socket) socket.close()
    socket = null
    activeRoom.value = null
    messages.value = []
    onlineUsers.value = new Set()
    typingUsers.value = new Map()
  }

  return {
    rooms, activeRoom, messages,
    onlineUsers, typingUsers, typingText,
    fetchRooms, joinRoom, leaveRoom,
    sendMessage, sendTyping,
  }
})