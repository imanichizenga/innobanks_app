// static/js/realtime_notifications.js
// FIXED: Robust WebSocket with proper error handling and URL fixing

(function() {
    'use strict';

    let notifSocket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000;
    let isConnecting = false;

    // Check if user is authenticated
    function isAuthenticated() {
        const userElement = document.querySelector('[data-user-authenticated]');
        return userElement && userElement.dataset.userAuthenticated === 'true';
    }

    function connectNotifications() {
        // Skip if not authenticated or already connecting
        if (!isAuthenticated() || isConnecting) {
            return;
        }

        isConnecting = true;

        const wsScheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = window.location.host;
        const wsUrl = `${wsScheme}//${wsHost}/ws/notifications/`;

        console.log('Attempting to connect to:', wsUrl);

        notifSocket = new WebSocket(wsUrl);

        notifSocket.onopen = function() {
            console.log('✅ Global Notification WebSocket CONNECTED');
            reconnectAttempts = 0;
            isConnecting = false;
        };

        notifSocket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                handleNotificationMessage(data);
            } catch (error) {
                console.error('❌ Error parsing notification message:', error);
            }
        };

        notifSocket.onclose = function(event) {
            console.log(`🔌 Notification WebSocket CLOSED (code: ${event.code})`);
            notifSocket = null;
            isConnecting = false;
            
            // Attempt reconnection
            if (reconnectAttempts < maxReconnectAttempts && isAuthenticated()) {
                reconnectAttempts++;
                console.log(`🔄 Reconnecting... (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                setTimeout(connectNotifications, reconnectDelay * reconnectAttempts);
            } else if (reconnectAttempts >= maxReconnectAttempts) {
                console.error('❌ Max reconnection attempts reached');
            }
        };

        notifSocket.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
            isConnecting = false;
        };
    }

    function handleNotificationMessage(data) {
        console.log('📨 Received notification:', data.type);
        
        switch(data.type) {
            case 'init_unread':
                updateUnreadCount(data.unread_count);
                updateRecentMessages(data.recent_messages);
                break;
                
            case 'new_message_notification':
                handleNewMessage(data);
                break;
                
            case 'update_unread_count':
                updateUnreadCount(data.unread_count);
                updateRecentMessages(data.recent_messages);
                break;
                
            default:
                console.warn('Unknown notification type:', data.type);
        }
    }

    function handleNewMessage(data) {
        const notifData = data.message;
        console.log('🆕 New message notification:', notifData);
        
        // Update everything
        updateUnreadCount(data.unread_count);
        updateRecentMessages(data.recent_messages);
        updateBadgeSymbols(data.unread_count);
        addMessageToDropdown(notifData);
        
        // Audio + Visual feedback
        playNotificationSound();
        showBrowserNotification(notifData);
        animateBadges();
    }

    function updateUnreadCount(count) {
        console.log(`🔢 Updating unread count to: ${count}`);
        
        // Profile dropdown badge
        const profileBadge = document.getElementById('global-unread-badge');
        if (profileBadge) {
            profileBadge.textContent = count;
            profileBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }
        
        // Notification bell badge
        const notifBadge = document.getElementById('notifications-badge-symbol');
        if (notifBadge) {
            notifBadge.textContent = count;
            notifBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }
        
        // Messages dropdown header
        const msgHeader = document.querySelector('#messageDropdown + .dropdown-menu h6');
        if (msgHeader) {
            const badgeHtml = count > 0 ? `<span class="badge bg-light text-dark ms-1">${count} New</span>` : '';
            msgHeader.innerHTML = `Messages ${badgeHtml}`;
        }
        
        // Notifications footer
        const notifFooter = document.querySelector('#notificationDropdown + .dropdown-menu h6:last-child');
        if (notifFooter) {
            const text = count > 0 ? `${count} new notifications` : 'See all notifications';
            const linkHtml = count > 0 ? '<br><a href="/chat/" class="small text-primary">View Chats</a>' : '';
            notifFooter.innerHTML = text + linkHtml;
        }
    }

    function updateBadgeSymbols(count) {
        const msgSymbol = document.getElementById('messages-badge-symbol');
        if (msgSymbol) {
            msgSymbol.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    function updateRecentMessages(messages) {
        console.log(`📝 Updating ${messages.length} recent messages`);
        updateMessagesDropdown(messages);
        updateNotificationsDropdown(messages.slice(0, 3));
    }

    function updateMessagesDropdown(messages) {
        const msgDropdown = document.querySelector('#messageDropdown + .dropdown-menu');
        if (!msgDropdown) return;
        
        // Clear existing messages (keep header & footer)
        const existingItems = msgDropdown.querySelectorAll('.dropdown-item.preview-item');
        existingItems.forEach(item => {
            const divider = item.nextElementSibling;
            if (divider && divider.classList.contains('dropdown-divider')) {
                divider.remove();
            }
            item.remove();
        });
        
        // Add new messages after first divider
        const firstDivider = msgDropdown.querySelector('.dropdown-divider');
        if (firstDivider) {
            messages.forEach(msg => {
                const msgHtml = createMessagePreviewHTML(msg);
                firstDivider.insertAdjacentHTML('afterend', msgHtml + '<div class="dropdown-divider"></div>');
            });
        }
    }

    function createMessagePreviewHTML(msg) {
        const photoHtml = msg.sender_photo 
            ? `<img src="${msg.sender_photo}" alt="image" class="profile-pic rounded-circle" style="width: 40px; height: 40px; object-fit: cover;">`
            : `<div class="profile-pic rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; font-size: 0.8rem;">
                ${msg.sender_username.charAt(0).toUpperCase()}
               </div>`;
        
        const newBadge = !msg.is_read ? '<span class="badge bg-primary small">New</span>' : '';
        const chatUrl = `/chat/${msg.sender_username}/`;
        
        return `
            <a class="dropdown-item preview-item" href="${chatUrl}">
                <div class="preview-thumbnail">${photoHtml}</div>
                <div class="preview-item-content d-flex align-items-start flex-column justify-content-center">
                    <h6 class="preview-subject ellipsis mb-1 font-weight-normal">${msg.sender_fullname} sent you a message</h6>
                    <p class="text-gray mb-0 small">${msg.message}</p>
                    <p class="text-gray mb-0 small">${msg.timestamp}</p>
                    ${newBadge}
                </div>
            </a>
        `;
    }

    function updateNotificationsDropdown(messages) {
        const notifDropdown = document.querySelector('#notificationDropdown + .dropdown-menu');
        if (!notifDropdown) return;
        
        // Remove existing message notifications
        const existingNotifs = notifDropdown.querySelectorAll('.dropdown-item.preview-item .mdi-message-text-outline');
        existingNotifs.forEach(icon => {
            const item = icon.closest('.dropdown-item');
            const divider = item.nextElementSibling;
            if (divider && divider.classList.contains('dropdown-divider')) {
                divider.remove();
            }
            item.remove();
        });
        
        // Add new ones after first divider
        const firstDivider = notifDropdown.querySelector('.dropdown-divider');
        if (firstDivider) {
            messages.forEach(msg => {
                const notifHtml = `
                    <a class="dropdown-item preview-item" href="/chat/${msg.sender_username}/">
                        <div class="preview-thumbnail">
                            <div class="preview-icon bg-info">
                                <i class="mdi mdi-message-text-outline"></i>
                            </div>
                        </div>
                        <div class="preview-item-content d-flex align-items-start flex-column justify-content-center">
                            <h6 class="preview-subject font-weight-normal mb-1">New message from ${msg.sender_fullname}</h6>
                            <p class="text-gray ellipsis mb-0 small">${msg.message}</p>
                        </div>
                    </a>
                    <div class="dropdown-divider"></div>
                `;
                firstDivider.insertAdjacentHTML('afterend', notifHtml);
            });
        }
    }

    function addMessageToDropdown(notifData) {
        const msgDropdown = document.querySelector('#messageDropdown + .dropdown-menu');
        if (!msgDropdown) return;
        
        const firstDivider = msgDropdown.querySelector('.dropdown-divider');
        if (!firstDivider) return;
        
        const photoHtml = notifData.sender_photo
            ? `<img src="${notifData.sender_photo}" alt="image" class="profile-pic rounded-circle" style="width: 40px; height: 40px; object-fit: cover;">`
            : `<div class="profile-pic rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; font-size: 0.8rem;">
                ${notifData.sender.charAt(0).toUpperCase()}
               </div>`;
        
        const newItemHtml = `
            <a class="dropdown-item preview-item" href="/chat/${notifData.sender}/">
                <div class="preview-thumbnail">${photoHtml}</div>
                <div class="preview-item-content d-flex align-items-start flex-column justify-content-center">
                    <h6 class="preview-subject ellipsis mb-1 font-weight-normal">${notifData.sender_fullname} sent you a message</h6>
                    <p class="text-gray mb-0 small">${notifData.message_preview}</p>
                    <p class="text-gray mb-0 small">Just now</p>
                    <span class="badge bg-primary small">New</span>
                </div>
            </a>
            <div class="dropdown-divider"></div>
        `;
        
        firstDivider.insertAdjacentHTML('afterend', newItemHtml);
        
        // Limit to 5 messages
        const items = msgDropdown.querySelectorAll('.dropdown-item.preview-item');
        if (items.length > 6) { // 5 + header
            const lastItem = items[items.length - 1];
            const lastDivider = lastItem.nextElementSibling;
            lastDivider?.remove();
            lastItem.remove();
        }
    }

    function playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(err => {
                console.log('🔇 Could not play notification sound:', err);
            });
        } catch (e) {
            console.log('🔇 No notification sound available');
        }
    }

    function showBrowserNotification(notifData) {
        if (!("Notification" in window)) return;
        
        if (Notification.permission === "granted") {
            new Notification(notifData.title, {
                body: notifData.body,
                icon: notifData.sender_photo || '/static/innobanks.png',
                tag: 'chat-message',
                requireInteraction: false,
                silent: false
            });
        }
    }

    function animateBadges() {
        const badges = [
            document.getElementById('global-unread-badge'),
            document.getElementById('notifications-badge-symbol'),
            document.getElementById('messages-badge-symbol')
        ];
        
        badges.forEach(badge => {
            if (badge && badge.style.display !== 'none') {
                badge.classList.add('animate__animated', 'animate__pulse', 'animate__infinite');
                setTimeout(() => {
                    badge.classList.remove('animate__animated', 'animate__pulse', 'animate__infinite');
                }, 2000);
            }
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Initializing real-time notifications...');
        
        // Request notification permission early
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission().then(permission => {
                console.log('🔔 Notification permission:', permission);
            });
        }
        
        // Connect if authenticated
        if (isAuthenticated()) {
            connectNotifications();
        }
    });

    // Auto-reconnect when tab becomes visible
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && (!notifSocket || notifSocket.readyState !== WebSocket.OPEN)) {
            console.log('👁️ Tab visible - reconnecting notifications');
            reconnectAttempts = 0;
            setTimeout(connectNotifications, 1000);
        }
    });

    // Auto-reconnect on page focus
    window.addEventListener('focus', function() {
        if (!notifSocket || notifSocket.readyState !== WebSocket.OPEN) {
            console.log('🎯 Window focused - reconnecting notifications');
            reconnectAttempts = 0;
            setTimeout(connectNotifications, 1000);
        }
    });

    // Expose for debugging
    window.NotificationsDebug = {
        connect: connectNotifications,
        status: () => notifSocket?.readyState,
        reconnectAttempts
    };

})();