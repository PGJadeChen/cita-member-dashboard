type Count = number;
type MonthYear = string;
type Amount = number;

export interface NameValuePair<T> {
    name: string;
    value: T;
}

export interface CityData {
    name: string;
    value: Count;
}

export interface RegionData {
    name: string;
    value: Count;
    children: CityData[];
}

export interface MapProps {
    data: RegionData[];
}

interface GeoLocation {
    latitude: number;
    longitude: number;
}

export interface KeyMetrics {
    totalMembers: Count;
    activeMembers: Count;
    newMembersThisMonth: Count;
}

export interface RegionDistribution {
    mainRegions: RegionData[];
    otherRegions: RegionData[];
}

export interface MembershipStatus {
    active: Count;
    expired: Count;
}

export interface MembershipType {
    thirtyDays: Count;
    sixtyDays: Count;
    fortyEightDays: Count;
}

export interface RenewalStatus {
    renewed: Count;
    notRenewed: Count;
}

export interface IncomeData extends NameValuePair<Amount> {
    month: MonthYear;
    amount: Amount;
}

export interface CityDistribution extends NameValuePair<Count>, GeoLocation {
    city: string;
    count: Count;
}

export interface ActivityData {
    dayOfWeek: number;
    hour: number;
    count: Count;
}

export interface NewMembersData extends NameValuePair<Count> {
    month: MonthYear;
    count: Count;
}

// MetricCard props
export interface MetricCardProps {
    title: string;
    value: Count | string;
}
