import React, { useState, useEffect } from 'react'
import { Card, Select, Spinner } from '@/components/ui'
import { 
    HiOutlineCurrencyDollar,
    HiOutlineShoppingCart,
    HiOutlineEye
} from 'react-icons/hi'
import ReactApexChart from 'react-apexcharts'
import { dashboardApi, AnalyticsOverviewResponse, AnalyticsTimeSeriesResponse } from '../api/apiDashboard'
import dayjs from 'dayjs'
import quarterOfYear from 'dayjs/plugin/quarterOfYear'

dayjs.extend(quarterOfYear)

const timeRanges = [
    { value: 'today', label: 'Today' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'yearly', label: 'Yearly' }
] as const;

type TimeRangeOption = typeof timeRanges[number];
type TimeRangeValue = TimeRangeOption['value'];

interface StatCardProps {
    icon: React.ElementType
    iconColor: string
    label: string
    value: string
    growthRate: string
    timeRange: string
    isSelected: boolean
    onClick: () => void
}

const StatCard = ({ 
    icon: Icon, 
    iconColor, 
    label, 
    value, 
    growthRate,
    timeRange, 
    isSelected,
    onClick 
}: StatCardProps) => {
    const iconBgColor = {
        'text-red-500': 'bg-red-100',
        'text-emerald-500': 'bg-emerald-100',
        'text-violet-500': 'bg-violet-100'
    }[iconColor] || 'bg-gray-100'

    return (
        <div 
            className={`cursor-pointer transition-all duration-200 rounded-lg p-6 ${
                isSelected ? 'bg-white shadow-lg' : 'bg-transparent'
            }`}
            onClick={onClick}
        >
            <div className="flex flex-col gap-4">
                <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${iconBgColor}`}>
                        <span className={`text-xl ${iconColor}`}>
                            <Icon />
                        </span>
                    </div>
                    <span className="text-sm text-gray-500">{label}</span>
                </div>
                <div>
                    <h3 className="font-bold text-2xl text-gray-900">{value}</h3>
                    <div className="flex items-center gap-1 mt-1">
                        <span className={`text-sm font-semibold ${
                            parseFloat(growthRate) >= 0 
                                ? 'text-success' 
                                : 'text-error'
                        }`}>
                            {parseFloat(growthRate) >= 0 ? '+' : ''}{growthRate}%
                        </span>
                        <span className="text-sm text-gray-500">from last {timeRange.toLowerCase()}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

const getChartData = (statId: 'New Leads' | 'Potential Leads' | 'Sales', timeRange: string) => {
    // Sample data - in real app, this would come from API based on statId and timeRange
    const data: Record<'New Leads' | 'Potential Leads' | 'Sales', Record<string, number[]>> = {
        'New Leads': {
            weekly: [21000, 22500, 21800, 22800, 21500, 23000, 21827],
            monthly: [19000, 20500, 21800, 22800, 21500, 23000, 21827],
        },
        'Potential Leads': {
            weekly: [1500, 1650, 1580, 1700, 1620, 1800, 1782],
            monthly: [1200, 1400, 1580, 1700, 1620, 1800, 1782],
        },
        Sales: {
            weekly: [800000, 820000, 815000, 830000, 810000, 840000, 832700],
            monthly: [750000, 780000, 815000, 830000, 810000, 840000, 832700],
        }
    }

    const colors: Record<'New Leads' | 'Potential Leads' | 'Sales', string> = {
        'New Leads': '#3B82F6', // blue-500
        'Potential Leads': '#10B981', // emerald-500
        Sales: '#8B5CF6' // violet-500
    }

    return {
        options: {
            chart: {
                type: 'line' as const,
                toolbar: { show: false },
                zoom: { enabled: false }
            },
            stroke: {
                curve: 'smooth' as const,
                width: 2,
                colors: [colors[statId]]
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.7,
                    opacityTo: 0.2,
                    stops: [0, 90, 100]
                }
            },
            xaxis: {
                categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as string[],
                labels: {
                    style: { colors: '#6B7280', fontSize: '12px' }
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: {
                    style: { colors: '#6B7280', fontSize: '12px' }
                }
            },
            grid: {
                borderColor: '#E5E7EB',
                strokeDashArray: 5,
                xaxis: { lines: { show: true } },
                yaxis: { lines: { show: true } },
                padding: { top: 0, right: 0, bottom: 0, left: 0 }
            },
            tooltip: {
                theme: 'light',
                x: { show: false },
                y: {
                    formatter: (value: number) => {
                        if (statId === 'New Leads') return `$${value.toLocaleString()}`
                        if (statId === 'Potential Leads') return `${(value/1000).toFixed(1)}K`
                        return value.toLocaleString()
                    }
                }
            }
        },
        series: [{
            name: statId.charAt(0).toUpperCase() + statId.slice(1),
            data: data[statId][timeRange] || data[statId].weekly
        }]
    }
}

function getDateRange(timeRange: TimeRangeValue): { start_date: string, end_date: string } {
    const now = dayjs();
    let start, end;
    switch (timeRange) {
        case 'today':
            start = now.startOf('day');
            end = now.endOf('day');
            break;
        case 'weekly':
            start = now.startOf('week');
            end = now.endOf('week');
            break;
        case 'monthly':
            start = now.startOf('month');
            end = now.endOf('month');
            break;
        case 'quarterly':
            start = now.startOf('quarter');
            end = now.endOf('quarter');
            break;
        case 'yearly':
            start = now.startOf('year');
            end = now.endOf('year');
            break;
        default:
            start = now.startOf('month');
            end = now.endOf('month');
    }
    return {
        start_date: start.format('YYYY-MM-DD'),
        end_date: end.format('YYYY-MM-DD'),
    };
}

const OverviewStats = () => {
    const [timeRange, setTimeRange] = useState<TimeRangeOption>(timeRanges[2]) // default to monthly
    const [selectedStat, setSelectedStat] = useState<'New Leads' | 'Potential Leads' | 'Sales'>('New Leads')
    const [analytics, setAnalytics] = useState<AnalyticsOverviewResponse | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [chartData, setChartData] = useState<AnalyticsTimeSeriesResponse | null>(null)
    const [chartLoading, setChartLoading] = useState(false)
    const [chartError, setChartError] = useState<string | null>(null)

    const fetchAnalytics = async (range: TimeRangeOption) => {
        setLoading(true)
        setError(null)
        try {
            const { start_date, end_date } = getDateRange(range.value)
            const response = await dashboardApi.getOverviewAnalytics({ start_date, end_date })
            setAnalytics(response)
        } catch (err) {
            setError('Failed to load analytics')
        } finally {
            setLoading(false)
        }
    }

    const fetchChartData = async (range: 'weekly' | 'yearly') => {
        setChartLoading(true)
        setChartError(null)
        try {
            const response = await dashboardApi.getTimeSeriesAnalytics(range)
            setChartData(response)
        } catch (err) {
            setChartError('Failed to load chart data')
        } finally {
            setChartLoading(false)
        }
    }

    useEffect(() => {
        fetchAnalytics(timeRange)
        if (timeRange.value === 'weekly' || timeRange.value === 'yearly') {
            fetchChartData(timeRange.value)
        } else {
            setChartData(null)
        }
    }, [timeRange])

    const stats = [
        {
            id: 'New Leads' as const,
            icon: HiOutlineCurrencyDollar,
            iconColor: 'text-blue-500',
            label: 'New Leads',
            value: analytics ? analytics.new_leads.toString() : '--',
            growthRate: ''
        },
        {
            id: 'Potential Leads' as const,
            icon: HiOutlineShoppingCart,
            iconColor: 'text-emerald-500',
            label: 'Potential Leads',
            value: analytics ? analytics.potential_leads.toString() : '--',
            growthRate: ''
        },
        {
            id: 'Sales' as const,
            icon: HiOutlineEye,
            iconColor: 'text-violet-500',
            label: 'Sales',
            value: analytics ? analytics.sales.toString() : '--',
            growthRate: ''
        }
    ]

    const getApiChartData = (statId: 'New Leads' | 'Potential Leads' | 'Sales') => {
        if (!chartData) return null
        let seriesData: number[] = []
        if (statId === 'New Leads') seriesData = chartData.new_leads
        else if (statId === 'Potential Leads') seriesData = chartData.potential_leads
        else if (statId === 'Sales') seriesData = chartData.sales
        const colors: Record<'New Leads' | 'Potential Leads' | 'Sales', string> = {
            'New Leads': '#3B82F6',
            'Potential Leads': '#10B981',
            Sales: '#8B5CF6'
        }
        return {
            options: {
                chart: {
                    type: 'line' as const,
                    toolbar: { show: false },
                    zoom: { enabled: false }
                },
                stroke: {
                    curve: 'smooth' as const,
                    width: 2,
                    colors: [colors[statId]]
                },
                fill: {
                    type: 'gradient',
                    gradient: {
                        shadeIntensity: 1,
                        opacityFrom: 0.7,
                        opacityTo: 0.2,
                        stops: [0, 90, 100]
                    }
                },
                xaxis: {
                    categories: chartData.labels,
                    labels: {
                        style: { colors: '#6B7280', fontSize: '12px' }
                    },
                    axisBorder: { show: false },
                    axisTicks: { show: false }
                },
                yaxis: {
                    labels: {
                        style: { colors: '#6B7280', fontSize: '12px' }
                    }
                },
                grid: {
                    borderColor: '#E5E7EB',
                    strokeDashArray: 5,
                    xaxis: { lines: { show: true } },
                    yaxis: { lines: { show: true } },
                    padding: { top: 0, right: 0, bottom: 0, left: 0 }
                },
                tooltip: {
                    theme: 'light',
                    x: { show: false },
                    y: {
                        formatter: (value: number) => value.toLocaleString()
                    }
                }
            },
            series: [{
                name: statId.charAt(0).toUpperCase() + statId.slice(1),
                data: seriesData
            }]
        }
    }

    return (
        <Card className="bg-white">
            <div className="p-6 space-y-6">
                <div className="flex justify-between items-center">
                    <h4 className="font-semibold text-lg">Overview</h4>
                    <Select 
                        value={timeRange}
                        onChange={val => setTimeRange(val as TimeRangeOption)}
                        options={timeRanges as unknown as TimeRangeOption[]}
                        getOptionLabel={option => option.label}
                        getOptionValue={option => option.value}
                        className="min-w-[120px] border border-gray-300 rounded-md"
                        size="sm"
                    />
                </div>
                <div className="bg-gray-50 rounded-lg">
                    {loading ? (
                        <div className="flex justify-center items-center h-24"><Spinner size="lg" /></div>
                    ) : error ? (
                        <div className="text-red-500 text-center py-4">{error}</div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
                            {stats.map(stat => (
                                <StatCard 
                                    key={stat.id}
                                    icon={stat.icon}
                                    iconColor={stat.iconColor}
                                    label={stat.label}
                                    value={stat.value}
                                    growthRate={stat.growthRate}
                                    timeRange={timeRange.value}
                                    isSelected={selectedStat === stat.id}
                                    onClick={() => setSelectedStat(stat.id)}
                                />
                            ))}
                        </div>
                    )}
                </div>
                {(timeRange.value === 'weekly' || timeRange.value === 'yearly') && (
                    <div className="bg-white rounded-lg">
                        {chartLoading ? (
                            <div className="flex justify-center items-center h-24"><Spinner size="lg" /></div>
                        ) : chartError ? (
                            <div className="text-red-500 text-center py-4">{chartError}</div>
                        ) : chartData ? (
                            <ReactApexChart 
                                {...getApiChartData(selectedStat)!}
                                height={350}
                                type="line"
                            />
                        ) : null}
                    </div>
                )}
            </div>
        </Card>
    )
}

export default OverviewStats 