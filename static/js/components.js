/**
 * COMPONENTS.JS
 * Reusable JavaScript components and utilities
 */

/**
 * Modal Component
 */
class Modal {
  constructor(modalId) {
    this.modal = document.getElementById(modalId);
    this.backdrop = null;
    if (!this.modal) {
      console.warn(`Modal with id "${modalId}" not found`);
      return;
    }
    this.init();
  }

  init() {
    // Create backdrop if it doesn't exist
    if (!this.modal.parentElement.classList.contains('modal-backdrop')) {
      this.backdrop = document.createElement('div');
      this.backdrop.className = 'modal-backdrop';
      this.backdrop.style.display = 'none';
      this.modal.parentElement.insertBefore(this.backdrop, this.modal);
      this.backdrop.appendChild(this.modal);
    } else {
      this.backdrop = this.modal.parentElement;
    }

    // Close on backdrop click
    this.backdrop.addEventListener('click', (e) => {
      if (e.target === this.backdrop) {
        this.close();
      }
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });

    // Close button
    const closeBtn = this.modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }
  }

  open() {
    if (this.backdrop) {
      this.backdrop.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }
  }

  close() {
    if (this.backdrop) {
      this.backdrop.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  isOpen() {
    return this.backdrop && this.backdrop.style.display === 'flex';
  }

  toggle() {
    if (this.isOpen()) {
      this.close();
    } else {
      this.open();
    }
  }
}

/**
 * Navigation Toggle
 */
function initNavigation() {
  const navToggle = document.querySelector('.app-nav-toggle');
  const navMenu = document.querySelector('.app-nav-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('open');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('open');
      }
    });
  }
}

/**
 * Toast/Notification Component
 */
function showToast(message, type = 'info', duration = 5000) {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type}`;
  toast.textContent = message;
  toast.style.position = 'fixed';
  toast.style.top = '20px';
  toast.style.right = '20px';
  toast.style.zIndex = '9999';
  toast.style.minWidth = '300px';
  toast.style.maxWidth = '500px';
  toast.style.animation = 'slideInRight 0.3s ease';

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease';
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, duration);
}

// Add toast animations to head if not present
if (!document.querySelector('#toast-animations')) {
  const style = document.createElement('style');
  style.id = 'toast-animations';
  style.textContent = `
    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
}

/**
 * Safe Content Setter (XSS Protection)
 * Use this instead of innerHTML for user-generated content
 */
function setSafeContent(element, content) {
  if (!element) return;
  
  // For plain text, use textContent
  element.textContent = content;
}

/**
 * Safe HTML Setter with DOMPurify (if available)
 * Use this for trusted HTML content
 */
function setSafeHTML(element, html) {
  if (!element) return;
  
  // If DOMPurify is available, use it
  if (typeof DOMPurify !== 'undefined') {
    element.innerHTML = DOMPurify.sanitize(html);
  } else {
    // Fallback: Use textContent for safety
    console.warn('DOMPurify not available, using textContent for safety');
    element.textContent = html.replace(/<[^>]*>/g, ''); // Strip HTML tags
  }
}

/**
 * Initialize all components on page load
 */
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  
  // Initialize all modals
  document.querySelectorAll('[id$="-modal"]').forEach((modal) => {
    new Modal(modal.id);
  });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    Modal,
    initNavigation,
    showToast,
    setSafeContent,
    setSafeHTML
  };
}

