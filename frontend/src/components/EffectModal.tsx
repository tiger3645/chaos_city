import React from 'react';
import { X, Zap } from 'lucide-react';
import { EffectChoice } from '../types/effects';

interface EffectModalProps {
    isOpen: boolean;
    message: string;
    choices: EffectChoice[];
    onChoose: (choice: EffectChoice) => void;
    onCancel?: () => void;
}

const EffectModal: React.FC<EffectModalProps> = ({
    isOpen,
    message,
    choices,
    onChoose,
    onCancel
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 animate-fade-in">
            <div className="bg-gray-900 rounded-lg p-6 max-w-2xl w-full mx-4 border-2 border-purple-500 shadow-2xl animate-scale-in">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <Zap className="w-6 h-6 text-purple-400" />
                        <h2 className="text-2xl font-bold text-white">Effect Choice</h2>
                    </div>
                    {onCancel && (
                        <button
                            onClick={onCancel}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    )}
                </div>

                {/* Message */}
                <div className="mb-6 p-4 bg-gray-800 rounded border border-purple-400">
                    <p className="text-lg text-white">{message}</p>
                </div>

                {/* Choices */}
                <div className="space-y-3 max-h-96 overflow-y-auto">
                    {choices.map((choice, index) => (
                        <button
                            key={choice.id || index}
                            onClick={() => onChoose(choice)}
                            className="w-full p-4 bg-gray-800 hover:bg-gray-700 border-2 border-gray-600 
                                     hover:border-purple-400 rounded-lg transition-all transform hover:scale-105
                                     text-left group"
                        >
                            <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 
                                              flex items-center justify-center text-white font-bold
                                              group-hover:bg-purple-500 transition-colors">
                                    {index + 1}
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-white mb-1">
                                        {choice.name}
                                    </h3>
                                    {choice.description && (
                                        <p className="text-sm text-gray-400">
                                            {choice.description}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </button>
                    ))}
                </div>

                {/* No choices available */}
                {choices.length === 0 && (
                    <div className="text-center py-8 text-gray-400">
                        <p>No choices available</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EffectModal;
