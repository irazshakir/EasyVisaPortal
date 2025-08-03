import React from 'react'
import { Card } from '@/components/ui'

const Settings = () => {
    return (
        <div className="h-full">
            <div className="container mx-auto">
                <div className="grid gap-4">
                    <Card>
                        <div className="p-4">
                            <h4 className="text-lg font-semibold mb-3">Settings</h4>
                            <p>Configure your application settings here.</p>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    )
}

export default Settings 