import ApiService from '@/services/ApiService'

export interface AnalyticsOverviewResponse {
    new_leads: number;
    potential_leads: number;
    sales: number;
    start_date: string;
    end_date: string;
}

export interface AnalyticsOverviewParams {
    start_date?: string; // format: YYYY-MM-DD
    end_date?: string;   // format: YYYY-MM-DD
}

export interface AnalyticsTimeSeriesResponse {
    labels: string[];
    new_leads: number[];
    potential_leads: number[];
    sales: number[];
}

export const dashboardApi = {
    getOverviewAnalytics: async (params?: AnalyticsOverviewParams) => {
        const response = await ApiService.fetchDataWithAxios<AnalyticsOverviewResponse>({
            url: '/api/v1/analytics/overview/',
            method: 'get',
            params,
        });
        return response;
    },
    getTimeSeriesAnalytics: async (range: 'weekly' | 'yearly') => {
        const response = await ApiService.fetchDataWithAxios<AnalyticsTimeSeriesResponse>({
            url: '/api/v1/analytics/timeseries/',
            method: 'get',
            params: { range },
        });
        return response;
    },
};
