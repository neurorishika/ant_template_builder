
#ifndef RESAMPLEIMAGEBYSPACING_H
#define RESAMPLEIMAGEBYSPACING_H

namespace ants
{
extern int
ResampleImageBySpacing(std::vector<std::string>, // equivalent to argv of command line parameters to main()
                       std::ostream * out_stream // [optional] output stream to write
);
} // namespace ants

#endif // RESAMPLEIMAGEBYSPACING_H
