import { defineStore } from 'pinia'
import { ref } from 'vue'
import en from '../locales/en.js'
import zh from '../locales/zh.js'
import ja from '../locales/ja.js'

const messages = { en, zh, ja }

export const useLocaleStore = defineStore('locale', () => {
  const current = ref(localStorage.getItem('locale') || 'en')

  function t(key) {
    const dict = messages[current.value] || messages.en
    const keys = key.split('.')
    let val = dict
    for (const k of keys) {
      if (val && typeof val === 'object' && k in val) {
        val = val[k]
      } else {
        return key
      }
    }
    return typeof val === 'string' ? val : key
  }

  function setLocale(lang) {
    current.value = lang
    localStorage.setItem('locale', lang)
  }

  return { current, t, setLocale }
})
