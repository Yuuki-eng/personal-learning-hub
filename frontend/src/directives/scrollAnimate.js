const observerMap = new WeakMap()

const ANIMATIONS = {
  'fade-up': {
    from: 'opacity: 0; transform: translateY(32px);',
    to: 'opacity: 1; transform: translateY(0);',
  },
  'fade-left': {
    from: 'opacity: 0; transform: translateX(-28px);',
    to: 'opacity: 1; transform: translateX(0);',
  },
  'fade-right': {
    from: 'opacity: 0; transform: translateX(28px);',
    to: 'opacity: 1; transform: translateX(0);',
  },
  'scale-in': {
    from: 'opacity: 0; transform: scale(0.92);',
    to: 'opacity: 1; transform: scale(1);',
  },
  'blur-in': {
    from: 'opacity: 0; filter: blur(6px); transform: translateY(16px);',
    to: 'opacity: 1; filter: blur(0); transform: translateY(0);',
  },
}

function parseArg(binding) {
  const val = binding.value
  if (typeof val === 'string') return { name: val, delay: 0, duration: 600 }
  if (typeof val === 'object') {
    return {
      name: val.name || 'fade-up',
      delay: val.delay || 0,
      duration: val.duration || 600,
    }
  }
  return { name: 'fade-up', delay: 0, duration: 600 }
}

export default {
  mounted(el, binding) {
    const { name, delay, duration } = parseArg(binding)
    const anim = ANIMATIONS[name] || ANIMATIONS['fade-up']

    el.style.cssText += anim.from
    el.style.transition = `opacity ${duration}ms cubic-bezier(0.22, 1, 0.36, 1), transform ${duration}ms cubic-bezier(0.22, 1, 0.36, 1), filter ${duration}ms ease`
    el.style.willChange = 'opacity, transform'

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setTimeout(() => {
              el.style.cssText += anim.to
            }, delay)
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    )

    observer.observe(el)
    observerMap.set(el, observer)
  },

  unmounted(el) {
    const observer = observerMap.get(el)
    if (observer) {
      observer.disconnect()
      observerMap.delete(el)
    }
  },
}
