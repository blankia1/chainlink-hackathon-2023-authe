import { useTranslate, useNavigation } from "@refinedev/core";
import { useSimpleList } from "@refinedev/antd";
import {
    Typography,
    List as AntdList,
    Tooltip,
    ConfigProvider,
    theme,
} from "antd";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

import { IEvent } from "interfaces";
import {
    TimelineContent,
    Timeline,
    TimelineItem,
    CreatedAt,
    Number,
} from "./styled";
import { useAccount } from 'wagmi'


dayjs.extend(relativeTime);

export const OrderTimeline: React.FC = () => {
    const t = useTranslate();
    const { show } = useNavigation();
    const { address, isConnected } = useAccount()

    const { listProps } = useSimpleList<IEvent>({
        resource: "events",
        meta: {"address": address},
        initialSorter: [
            {
                field: "createdAt",
                order: "desc",
            },
        ],
        pagination: {
            pageSize: 6,
        },
        syncWithLocation: false,
    });

    const { dataSource } = listProps;

    const { Text } = Typography;

    const orderStatusColor = (
        id: string,
    ):
        | { indicatorColor: string; backgroundColor: string; text: string }
        | undefined => {
        switch (id) {
            case "1":
                return {
                    indicatorColor: "orange",
                    backgroundColor: "#fff7e6",
                    text: "Critical:",
                };
            case "2":
                return {
                    indicatorColor: "red",
                    backgroundColor: "#fff1f0",
                    text: "Error:",
                };
            case "3":
                return {
                    indicatorColor: "orange",
                    backgroundColor: "#fff7e6",
                    text: "Warning:",
                };
            case "4":
                return {
                    indicatorColor: "blue",
                    backgroundColor: "#e6f7ff",
                    text: "Info:",
                };
            case "5":
                return {
                    indicatorColor: "green",
                    backgroundColor: "#e6fffb",
                    text: "Success:",
                };
            default:
                break;
        }
    };

    return (
        
        <AntdList
            {...listProps}
            pagination={{
                ...listProps.pagination,
                simple: true,
            }}
        >
            <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
                <Timeline>
                    {dataSource?.map(
                        ({ criticality_level, created_at, chain, message_summary, message, link_id, resource }) => (
                            <TimelineItem
                                key={created_at}
                                color={
                                    orderStatusColor(criticality_level.toString())
                                        ?.indicatorColor
                                }
                            >
                                <TimelineContent
                                    backgroundColor={
                                        orderStatusColor(criticality_level.toString())
                                            ?.backgroundColor || "transparent"
                                    }
                                >
                                    <Tooltip
                                        overlayInnerStyle={{ color: "#626262" }}
                                        color="rgba(255, 255, 255, 0.3)"
                                        placement="topLeft"
                                        title={dayjs.unix(created_at).format("lll")}
                                    >
                                        <CreatedAt italic>
                                            {dayjs.unix(created_at).fromNow()}
                                        </CreatedAt>
                                    </Tooltip>
                                    <Text>
                                        {t(
                                            `${
                                                orderStatusColor(
                                                    criticality_level.toString(),
                                                )?.text
                                            }`,
                                        )}
                                    </Text>
                                    <Text>
                                        {message_summary}
                                    </Text>
                                    <Number
                                        onClick={() => show(resource, link_id)}
                                        strong
                                    >
                                        #{link_id}
                                    </Number>
                                </TimelineContent>
                            </TimelineItem>
                        ),
                    )}
                </Timeline>
            </ConfigProvider>
        </AntdList>
       
    );
};