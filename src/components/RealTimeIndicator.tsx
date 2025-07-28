import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

interface RealTimeIndicatorProps {
  isConnected: boolean;
  lastUpdate?: string;
}

export const RealTimeIndicator: React.FC<RealTimeIndicatorProps> = ({ 
  isConnected, 
  lastUpdate 
}) => {
  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`flex items-center gap-1 ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
        {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
        <span>{isConnected ? 'Live Data' : 'Offline'}</span>
      </div>
      {lastUpdate && (
        <span className="text-gray-400">
          Updated: {lastUpdate}
        </span>
      )}
    </div>
  );
};