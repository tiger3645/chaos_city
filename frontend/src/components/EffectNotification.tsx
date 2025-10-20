import React, { useEffect, useState } from 'react';
import { Zap, X } from 'lucide-react';

export interface EffectNotification {
    id: string;
    message: string;
    type?: 'effect' | 'trigger' | 'info';
    duration?: number;
}

interface EffectNotificationProps {
    notification: EffectNotification;
    onDismiss: (id: string) => void;
}

const EffectNotificationItem: React.FC<EffectNotificationProps> = ({
    notification,
    onDismiss
}) => {
    const [isExiting, setIsExiting] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsExiting(true);
            setTimeout(() => onDismiss(notification.id), 300);
        }, notification.duration || 3000);

        return () => clearTimeout(timer);
    }, [notification, onDismiss]);

    const getTypeColor = () => {
        switch (notification.type) {
            case 'trigger':
                return 'border-yellow-400 bg-yellow-900';
            case 'info':
                return 'border-blue-400 bg-blue-900';
            default:
                return 'border-purple-400 bg-purple-900';
        }
    };

    return (
        <div
            className={`${getTypeColor()} bg-opacity-90 border-2 rounded-lg p-4 shadow-lg
                       transform transition-all duration-300 max-w-md
                       ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}`}
        >
            <div className="flex items-start gap-3">
                <Zap className="w-5 h-5 flex-shrink-0 mt-0.5 text-white" />
                <p className="flex-1 text-white text-sm leading-tight">
                    {notification.message}
                </p>
                <button
                    onClick={() => {
                        setIsExiting(true);
                        setTimeout(() => onDismiss(notification.id), 300);
                    }}
                    className="text-gray-300 hover:text-white transition-colors flex-shrink-0"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
};

interface EffectNotificationsContainerProps {
    notifications: EffectNotification[];
    onDismiss: (id: string) => void;
}

export const EffectNotificationsContainer: React.FC<EffectNotificationsContainerProps> = ({
    notifications,
    onDismiss
}) => {
    return (
        <div className="fixed top-4 right-4 z-40 space-y-3 pointer-events-none">
            {notifications.map(notification => (
                <div key={notification.id} className="pointer-events-auto">
                    <EffectNotificationItem
                        notification={notification}
                        onDismiss={onDismiss}
                    />
                </div>
            ))}
        </div>
    );
};

export default EffectNotificationItem;
